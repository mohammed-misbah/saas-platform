from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    company_id: int | None = None
    project_name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    project_name: str
    description: str | None = None
    status: str


class ProjectResponse(BaseModel):
    id: int
    company_id: int
    project_name: str
    description: str | None
    status: str
    created_by: int

    class Config:
        from_attributes = True



#Assign a users to projects
class ProjectMemberCreate(BaseModel):
    user_id: int


class ProjectMemberResponse(BaseModel):
    user_id: int
    email: str
    company_id: int
    project_name: str
    description: str | None
    project_status: str

    class Config:
        from_attributes = True