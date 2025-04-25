# OrgChart Service

A FastAPI-based microservice to manage and explore organizational hierarchies.

---

## 1. Quick Start (Docker Compose)

```bash
cd orgchart-service
docker-compose up --build
```
The service runs on `http://localhost:8000`

## 2. Database Initialization & Seeding

call `GET http://localhost:8000/api/v1/seed-data/populate`


## 3. Hierarchy Logic
Endpoints Implemented:
Business use cases may require either only direct reports or full hierarchy traversal, so both are supported.


- Direct Reports: 
  
   `GET /api/v1/orgcharts/{org_id}/employees/{employee_id}/direct_reports`
  
- Manager Chain (All Reportees):
  
    `GET /api/v1/orgcharts/{org_id}/employees/{employee_id}/manager_chain`
  
## 4. Deletion & CEO Rules
- CEO Protection : If the employee is a CEO (manager_id IS NULL), deletion is blocked with:
`Cannot delete CEO. Use promote endpoint instead.`
- Re-parenting Logic:
    - When a non-CEO employee is deleted, all their reports (direct + indirect) are reassigned to the deleted employee’s manager.
    - Done atomically within a transaction.
    

## 5. Scaling Notes
Indexes Added:
- on organisation id
- on employee id
These help recursive queries and lookups stay fast even with large datasets.

## 6. Performance Evidence
Benchmarked locally with:
- 13,000+ organizations
- ~135,000 employees

API Performance Example:

`GET /api/v1/orgcharts/10101/employees` => 0.024s

Average API response time: ~0.025s

Max observed latency: 0.054s


## 7. Potential Enhancements
- Add table partitioning on `org_id` to efficiently read from millions of records.
- Introduce pagination for large result sets.
- Consider rewriting in Spring Boot for better JVM performance at scale.
- Add frontend for org chart visualization.
- Implement role-based access control.

## 8. AI Usage

Used AI to:

- design decisions
- Design recursive logic
- Write FastAPI models and endpoints
- Improve structure and readability

---

# Data Analysis Queries:

### 1. Query to get each organization and its CEO:

```
SELECT 
    o.id AS org_id,
    o.name AS organization_name,
    e.id AS ceo_id,
    e.name AS ceo_name,
    e.title AS ceo_title
FROM org_charts o
JOIN employees e ON e.org_id = o.id
WHERE e.manager_id IS NULL;

```

### 2. Query to get employee count for each organization

```
SELECT 
    o.id AS org_id,
    o.name AS organization_name,
    COUNT(e.id) AS employee_count
FROM org_charts o
JOIN employees e ON e.org_id = o.id
GROUP BY o.id
ORDER BY employee_count DESC;
```

### 3. Employees with no reportees (individual contributors)
```
SELECT 
    e.id,
    e.name,
    e.title,
    e.org_id
FROM employees e
LEFT JOIN employees r ON r.manager_id = e.id
WHERE r.id IS NULL AND e.manager_id IS NOT NULL;
```
