from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService
from app.api.deps import get_db
from app.models.employee import Employee

router = APIRouter()


@router.post("/{org_id}/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(org_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    return EmployeeService.create_employee(db, org_id, employee)


@router.get("/{org_id}/employees", response_model=List[EmployeeResponse])
def read_employees(org_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return EmployeeService.get_employees(db, org_id, skip=skip, limit=limit)


@router.get("/{org_id}/employees/{employee_id}", response_model=EmployeeResponse)
def read_employee(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_employee(db, org_id, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee


@router.put("/{org_id}/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
        org_id: int,
        employee_id: int,
        employee: EmployeeUpdate,
        db: Session = Depends(get_db)
):
    updated_employee = EmployeeService.update_employee(db, org_id, employee_id, employee)
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return updated_employee


@router.delete("/{org_id}/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    if not EmployeeService.delete_employee(db, org_id, employee_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return None


@router.put("/{org_id}/employees/{employee_id}/promote", response_model=EmployeeResponse)
def promote_to_ceo(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    return EmployeeService.promote_to_ceo(db, org_id, employee_id)


@router.get("/{org_id}/employees/{employee_id}/direct_reports", response_model=List[EmployeeResponse])
def get_direct_reports(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    # Get employee with reports loaded
    employee = EmployeeService.get_direct_reports(db, org_id, employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not direct reports"
        )

    # Explicit query for direct reports (more reliable than relationship)
    direct_reports = db.query(Employee).filter(
        Employee.org_id == org_id,
        Employee.manager_id == employee_id
    ).all()

    return direct_reports


@router.get("/{org_id}/employees/{employee_id}/manager_chain")
def get_all_reportees(org_id: int, employee_id: int, db: Session = Depends(get_db)):
    return EmployeeService.get_all_reportees(db, org_id, employee_id)
