from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db, get_current_user
from app.models.projects import Project
from app.models.role import Role
from app.models.user import User

from app.schemas.project import (
    ProjectMemberCreate,
    ProjectMemberResponse
)

from app.audit.audit_service import create_audit_log
from app.models.project_members import ProjectMember


router = APIRouter(
    prefix="/assign_projects",
    tags=["Assign Projects"]
)

# Assign a users to projects

@router.post("/{project_id}/members")
def assign_user_to_project(
    project_id: int,
    member_data: ProjectMemberCreate,
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

    user = (
        db.query(User)
        .filter(
            User.id == member_data.user_id,
            User.company_id == project.company_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found in this company"
        )

    assigned_user_role = (
        db.query(Role)
        .filter(Role.id == user.role_id)
        .first()
    )

    if not assigned_user_role:
        raise HTTPException(
            status_code=404,
            detail="Assigned user role not found"
        )

    if assigned_user_role.role_name in [
        "Super Admin",
        "Company Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only Members can be assigned to projects"
        )

    existing_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_data.user_id
        )
        .first()
    )

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="User already assigned to project"
        )

    project_member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id
    )

    db.add(project_member)
    db.commit()

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=project.company_id,
        action=f"Assigned user {user.email} to project {project.project_name}"
    )

    return {
        "message": "User assigned successfully"
    }




@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def get_project_members(
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

    members = (
        db.query(User)
        .join(
            ProjectMember,
            User.id == ProjectMember.user_id
        )
        .filter(
            ProjectMember.project_id == project_id
        )
        .all()
    )

    response = []

    for member in members:

        response.append(
            {
                "user_id": member.id,
                "email": member.email,
                "company_id": member.company_id,

                "project_name": project.project_name,
                "description": project.description,

                "project_status": project.status
            }
        )

    return response



@router.delete("/{project_id}/members/{user_id}")
def remove_user_from_project(
    project_id: int,
    user_id: int,
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

    if role.role_name not in [
        "Super Admin",
        "Company Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    # Project Validation

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

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Project member not found"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    db.delete(member)
    db.commit()

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=project.company_id,
        action=f"Removed user {user.email} from project {project.project_name}"
    )

    return {
        "message": "User removed from project successfully"
    }