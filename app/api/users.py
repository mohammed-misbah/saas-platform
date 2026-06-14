from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Request
from app.db.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password
from app.models.role import Role
from app.audit.audit_service import create_audit_log

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active
    }

@router.get("/tenant-test")
def tenant_test(
    current_user: User = Depends(get_current_user)
):
    return {
        "email": current_user.email,
        "company_id": current_user.company_id
    }

@router.post("/create")
def create_user(user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Get current user role
    role = (db.query(Role).filter(Role.id == current_user.role_id).first())

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    # Only Super Admin & Company Admin can create users
    if role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    # Get role being assigned to new user
    new_role = (
        db.query(Role)
        .filter(Role.id == user_data.role_id)
        .first()
    )

    if not new_role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    # Company Admin cannot create Admins
    if (
        role.role_name == "Company Admin"
        and new_role.role_name in ["Super Admin", "Company Admin"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Company Admin can only create Members"
        )

    # Check duplicate email
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role_id=user_data.role_id,
        company_id=current_user.company_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=current_user.company_id,
        action=f"Created user {user.email}"
    )

    return {
        "message": "User created successfully",
        "details": {
            "id": user.id,
            "email": user.email,
            "role_id": user.role_id,
            "company_id": user.company_id
        }
    }


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    if role.role_name == "Super Admin":

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    else:

        user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.company_id == current_user.company_id
            )
            .first()
        )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.email = user_data.email
    user.role_id = user_data.role_id

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=user.company_id,
        action=f"Updated user {user.email}"
    )

    return {
        "message": "User updated successfully"
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    if role.role_name == "Super Admin":

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    else:

        user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.company_id == current_user.company_id
            )
            .first()
        )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=user.company_id,
        action=f"Deleted user {user.email}"
    )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }



@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    if role.role_name == "Super Admin":

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    else:

        user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.company_id == current_user.company_id
            )
            .first()
        )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.get("/")
def get_users_list(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    if role.role_name == "Super Admin":

        users_list = (
            db.query(User)
            .all()
        )

    else:

        users_list = (
            db.query(User)
            .filter(
                User.company_id == current_user.company_id
            )
            .all()
        )

    return users_list