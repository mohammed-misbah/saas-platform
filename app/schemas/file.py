from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    id: int
    company_id: int
    project_id: int
    uploaded_by: int
    file_name: str
    file_url: str
    file_size: int
    content_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    message: str
    file: FileResponse