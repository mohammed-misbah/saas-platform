from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db, get_current_user
from app.models.projects import Project
from app.models.role import Role
from app.models.user import User

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectMemberCreate
)

from app.audit.audit_service import create_audit_log
from app.models.project_members import ProjectMember
from app.constants.project_constants import ALLOWED_STATUS_FLOW


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/create", response_model=ProjectResponse)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    if role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    # --------------------------------
    # Company Selection Logic
    # --------------------------------

    if role.role_name == "Super Admin":

        if not project_data.company_id:
            raise HTTPException(
                status_code=400,
                detail="Company ID is required"
            )

        company_id = project_data.company_id

    else:

        company_id = current_user.company_id

    # --------------------------------
    # Duplicate Project Check
    # --------------------------------

    existing_project = (
        db.query(Project)
        .filter(
            Project.company_id == company_id,
            Project.project_name == project_data.project_name
        )
        .first()
    )

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project already exists"
        )

    # --------------------------------
    # Create Project
    # --------------------------------

    project = Project(
        company_id=company_id,
        project_name=project_data.project_name,
        description=project_data.description,
        status="pending",
        created_by=current_user.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
        action=f"Created project {project.project_name}"
    )

    return project




@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    if role.role_name == "Super Admin":

        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    else:

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.company_id == current_user.company_id
            )
            .first()
        )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project



@router.get("/", response_model=list[ProjectResponse])
def get_project_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    if role.role_name == "Super Admin":

        projects = (
            db.query(Project)
            .all()
        )

    else:

        projects = (
            db.query(Project)
            .filter(
                Project.company_id == current_user.company_id
            )
            .all()
        )

    return projects



@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    if role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    if role.role_name == "Super Admin":

        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    else:

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.company_id == current_user.company_id
            )
            .first()
        )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    existing_project = (
        db.query(Project)
        .filter(
            Project.company_id == project.company_id,
            Project.project_name == project_data.project_name,
            Project.id != project.id
        )
        .first()
    )

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project already exists"
        )

    if project_data.status not in [
        "pending",
        "inprogress",
        "completed",
        "archived"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid project status"
        )
    
    current_status = project.status
    new_status = project_data.status

    if current_status != new_status:
        allowed_next_status = ALLOWED_STATUS_FLOW[current_status]

        if new_status not in allowed_next_status:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from {current_status} to {new_status}"
            )

    project.project_name = project_data.project_name
    project.description = project_data.description
    project.status = project_data.status

    db.commit()
    db.refresh(project)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=project.company_id,
        action=f"Updated project {project.project_name}"
    )

    return project



@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    if role.role_name not in ["Super Admin", "Company Admin"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    if role.role_name == "Super Admin":

        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    else:

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.company_id == current_user.company_id
            )
            .first()
        )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=project.company_id,
        action=f"Deleted project {project.project_name}"
    )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }





