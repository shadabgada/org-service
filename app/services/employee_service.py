from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.utils.hierarchy import get_all_reports

class EmployeeService:
    @staticmethod
    def get_employee(db: Session, org_id: int, employee_id: int):
        query = db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.org_id == org_id
        )
        return query.first()

    @staticmethod
    def get_direct_reports(db: Session, org_id: int, employee_id: int):
        return db.query(Employee).filter(
            Employee.manager_id == employee_id,
            Employee.org_id == org_id
        ).all()

    def get_all_reportees(db: Session, org_id: int, employee_id: int ):
        print(f"Params => employee_id={employee_id}, org_id={org_id}")
        query = text("""
            WITH RECURSIVE reportees AS (
                SELECT id, name, manager_id, org_id
                FROM employees
                WHERE manager_id = :employee_id AND org_id = :org_id

                UNION ALL

                SELECT e.id, e.name, e.manager_id, e.org_id
                FROM employees e
                INNER JOIN reportees r ON e.manager_id = r.id
            )
            SELECT * FROM reportees;
        """)

        result = db.execute(query, {
            "employee_id": employee_id,
            "org_id": org_id
        })
        rows = result.fetchall()
        print(f"Rows fetched => {rows}")
        return [dict(row._mapping) for row in rows]

    @staticmethod
    def get_employees(db: Session, org_id: int, skip: int = 0, limit: int = 100):
        return db.query(Employee).filter(
            Employee.org_id == org_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create_employee(db: Session, org_id: int, employee: EmployeeCreate):
        if employee.manager_id:
            manager = db.query(Employee).filter(
                Employee.id == employee.manager_id,
                Employee.org_id == org_id
            ).first()
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Manager not found in the same organization"
                )

        db_employee = Employee(**employee.dict(), org_id=org_id)
        db.add(db_employee)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid employee data"
            )
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def update_employee(db: Session, org_id: int, employee_id: int, employee: EmployeeUpdate):
        db_employee = db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.org_id == org_id
        ).first()
        if not db_employee:
            return None

        update_data = employee.dict(exclude_unset=True)
        if 'manager_id' in update_data:
            if update_data['manager_id'] == employee_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee cannot be their own manager"
                )
            if update_data['manager_id']:
                manager = db.query(Employee).filter(
                    Employee.id == update_data['manager_id'],
                    Employee.org_id == org_id
                ).first()
                if not manager:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Manager not found in the same organization"
                    )

        for field, value in update_data.items():
            setattr(db_employee, field, value)

        try:
            db.commit()
            db.refresh(db_employee)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid employee data"
            )
        return db_employee

    @staticmethod
    def delete_employee(db: Session, org_id: int, employee_id: int) -> bool:
        employee = db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.org_id == org_id
        ).first()

        if not employee:
            return False

        if employee.manager_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete CEO. Use promote endpoint instead."
            )

        try:
            # Get all reports before deletion
            reports = get_all_reports(db, employee_id)

            # Re-parent all reports
            for report in reports:
                print(
                    f"↪️ Reassigning employee {report['id']} from manager {report['manager_id']} to {employee.manager_id}")
                db.query(Employee).filter(Employee.id == report["id"]).update({
                    "manager_id": employee.manager_id
                })

            db.delete(employee)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Deletion failed: {str(e)}"
            )

    @staticmethod
    def promote_to_ceo(db: Session, org_id: int, employee_id: int):
        current_ceo = db.query(Employee).filter(
            Employee.org_id == org_id,
            Employee.manager_id.is_(None)
        ).first()
        if not current_ceo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CEO found for this organization"
            )

        new_ceo = db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.org_id == org_id
        ).first()
        if not new_ceo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        if new_ceo.id == current_ceo.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee is already the CEO"
            )

        # Reassign current CEO's reports to new CEO
        current_ceo_reports = db.query(Employee).filter(
            Employee.manager_id == current_ceo.id,
            Employee.org_id == org_id
        ).all()
        for report in current_ceo_reports:
            report.manager_id = new_ceo.id

        # Update new CEO to have no manager
        new_ceo.manager_id = None

        # Make current CEO report to new CEO
        current_ceo.manager_id = new_ceo.id

        db.commit()
        return new_ceo