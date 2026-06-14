from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.company import Company
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse
)
from app.models.user import User
from app.models.role import Role
from app.db.dependencies import get_db, get_current_user
from app.audit.audit_service import create_audit_log


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)

@router.post("/", response_model=CompanyResponse)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name != "Super Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Super Admin can create companies"
        )

    company = Company(
        company_name=company_data.company_name,
        slug=company_data.slug
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=company.id,
        action=f"Created company {company.company_name}"
    )

    return company


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name != "Super Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Super Admin can view companies"
        )

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name != "Super Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Super Admin can update companies"
        )

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    company.company_name = company_data.company_name
    company.slug = company_data.slug
    company.is_active = company_data.is_active

    db.commit()
    db.refresh(company)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=company.id,
        action=f"Updated company {company.company_name}"
    )

    return company



@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Only Super Admin can delete companies
    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name != "Super Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Super Admin can delete companies"
        )

    # Check company exists
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    # Check whether company has users
    users_exist = (
        db.query(User)
        .filter(User.company_id == company_id)
        .first()
    )

    if users_exist:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete company because it contains users"
        )
    
    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=current_user.company_id,
        action=f"Deleted company {company.company_name}"
    )

    # Delete company
    db.delete(company)
    db.commit()

    return {
        "message": "Company deleted successfully"
    }