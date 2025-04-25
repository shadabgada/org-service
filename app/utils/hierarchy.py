from sqlalchemy.orm import Session
from app.models.employee import Employee  # Add this import
from typing import List

from sqlalchemy.sql import text

def get_all_reports(db: Session, employee_id: int) -> list:
    query = text("""
        WITH RECURSIVE subordinates AS (
            SELECT id, name, title, manager_id, org_id
            FROM employees
            WHERE manager_id = :employee_id

            UNION ALL

            SELECT e.id, e.name, e.title, e.manager_id, e.org_id
            FROM employees e
            INNER JOIN subordinates s ON e.manager_id = s.id
        )
        SELECT * FROM subordinates;
    """)

    result = db.execute(query, {"employee_id": employee_id})
    rows = result.fetchall()
    print(f"📦 Total reports found: {len(rows)}")
    # for row in rows:
    #     print(f"➡️  Reportee ID: {row.id}, Name: {row.name}, Title: {row.title}, Reports To: {row.manager_id}")

    # Optionally map to Employee model objects (or return as dicts)
    return [dict(row._mapping) for row in rows]

# def get_all_reports(db: Session, manager_id: int) -> List:
#     """Recursively get all reports (direct and indirect) for a manager"""
#     all_reports = []
#
#     # Get direct reports
#     direct_reports = db.query(Employee).filter(Employee.manager_id == manager_id).all()
#     all_reports.extend(direct_reports)
#
#     # Recursively get reports of reports
#     for report in direct_reports:
#         all_reports.extend(get_all_reports(db, report.id))
#
#     return all_reports


def is_cycle_possible(db: Session, employee_id: int, new_manager_id: int) -> bool:
    """Check if assigning new_manager_id would create a cycle"""
    if new_manager_id is None:
        return False

    # Get all managers in the chain for the new manager
    managers = set()
    current_id = new_manager_id

    while current_id is not None:
        if current_id == employee_id:
            return True
        manager = db.query(Employee).get(current_id)
        if not manager:
            break
        current_id = manager.manager_id

    return False