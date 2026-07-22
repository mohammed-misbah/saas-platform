from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile
from app.db.dependencies import get_db, get_current_user
from app.models.projects import Project
from sqlalchemy.orm import Session

from app.models.file import File
from app.models.role import Role
from app.models.user import User

from app.schemas.file import (FileResponse, FileUploadResponse)
from app.storage.s3_service import (upload_file, delete_file, get_file_url)
from app.audit.audit_service import create_audit_log
from app.constants.file_constants import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE
import os


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post("/upload", response_model=FileUploadResponse)
def upload_project_file(project_id: int,file: UploadFile = FastAPIFile(...),db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    # Get Current User Role

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

    # Permission Check

    if role.role_name not in [
        "Super Admin",
        "Company Admin",
        "Member"
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
            detail="Invalid project or insufficient permissions."
        )

    # Archived Project Check

    if project.status == "archived":
        raise HTTPException(
            status_code=400,
            detail="Cannot upload files to an archived project."
        )
    # File Size Validation

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )

    # File Size Validation

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must not exceed 10 MB."
        )

    # Upload File To AWS S3

    file_key = upload_file(
        file=file,
        company_id=project.company_id,
        project_id=project.id
    )

    db_file = File(
        company_id=project.company_id,
        project_id=project.id,
        uploaded_by=current_user.id,
        file_name=file.filename,
        file_url=file_key,
        file_size=file_size,
        content_type=file.content_type
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # Audit Log

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=project.company_id,
        action=f"Uploaded file {db_file.file_name}"
    )

    return {
        "message": "File uploaded successfully",
        "file": db_file
    }


@router.get("/",response_model=list[FileResponse])
def get_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Get Current User Role

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

    # Permission Check

    if role.role_name not in [
        "Super Admin",
        "Company Admin",
        "Member"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    # Get Files

    if role.role_name == "Super Admin":

        files = (
            db.query(File)
            .all()
        )

    else:

        files = (
            db.query(File)
            .filter(
                File.company_id == current_user.company_id
            )
            .all()
        )

    # Generate Download URL

    response = []

    for file in files:

        response.append(
            FileResponse(
                id=file.id,
                company_id=file.company_id,
                project_id=file.project_id,
                uploaded_by=file.uploaded_by,
                file_name=file.file_name,
                file_url=get_file_url(file.file_url),
                file_size=file.file_size,
                content_type=file.content_type,
                created_at=file.created_at
            )
        )

    return response



@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Get Current User Role

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

    # Permission Check

    if role.role_name not in [
        "Super Admin",
        "Company Admin",
        "Member"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    # Get File

    if role.role_name == "Super Admin":

        file = (
            db.query(File)
            .filter(
                File.id == file_id
            )
            .first()
        )

    else:

        file = (
            db.query(File)
            .filter(
                File.id == file_id,
                File.company_id == current_user.company_id
            )
            .first()
        )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    # Generate Download URL

    download_url = get_file_url(file.file_url)

    # Return Response

    return FileResponse(
        id=file.id,
        company_id=file.company_id,
        project_id=file.project_id,
        uploaded_by=file.uploaded_by,
        file_name=file.file_name,
        file_url=download_url,
        file_size=file.file_size,
        content_type=file.content_type,
        created_at=file.created_at
    )
    

@router.get("/project/{project_id}", response_model=list[FileResponse])
def get_project_files(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Get Current User Role

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


    # Permission Check

    if role.role_name not in [
        "Super Admin",
        "Company Admin",
        "Member"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    # Validate Project

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
            detail="Project not found or access denied."
        )

    # Get Files

    files = (
        db.query(File)
        .filter(File.project_id == project_id)
        .all()
    )

    # Generate Download URLs

    response = []

    for file in files:

        response.append(
            FileResponse(
                id=file.id,
                company_id=file.company_id,
                project_id=file.project_id,
                uploaded_by=file.uploaded_by,
                file_name=file.file_name,
                file_url=get_file_url(file.file_url),
                file_size=file.file_size,
                content_type=file.content_type,
                created_at=file.created_at
            )
        )

    return response


@router.get("/company/{company_id}",response_model=list[FileResponse])
def get_company_files(company_id: int,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Get Current User Role
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

    # Only Super Admin

    if role.role_name != "Super Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Super Admin can view company files."
        )

    # Get Company Files

    files = (
        db.query(File)
        .filter(
            File.company_id == company_id
        )
        .all()
    )

    # Generate Download URLs

    response = []

    for file in files:

        response.append(
            FileResponse(
                id=file.id,
                company_id=file.company_id,
                project_id=file.project_id,
                uploaded_by=file.uploaded_by,
                file_name=file.file_name,
                file_url=get_file_url(file.file_url),
                file_size=file.file_size,
                content_type=file.content_type,
                created_at=file.created_at
            )
        )

    return response


@router.delete("/{file_id}")
def delete_uploaded_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Get Current User Role

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

    # Permission Check

    if role.role_name not in [
        "Super Admin",
        "Company Admin",
        "Member"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    # Get File

    if role.role_name == "Super Admin":

        db_file = (
            db.query(File)
            .filter(
                File.id == file_id
            )
            .first()
        )

    else:

        db_file = (
            db.query(File)
            .filter(
                File.id == file_id,
                File.company_id == current_user.company_id
            )
            .first()
        )

    if not db_file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    # Member Ownership Check

    if (
        role.role_name == "Member"
        and db_file.uploaded_by != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only delete files uploaded by you."
        )

    # Delete File From AWS S3

    delete_file(
        db_file.file_url
    )

    # Audit Log

    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=db_file.company_id,
        action=f"Deleted file {db_file.file_name}"
    )

    # Delete Database Record

    db.delete(db_file)
    db.commit()

    return {
        "message": "File deleted successfully"
    }