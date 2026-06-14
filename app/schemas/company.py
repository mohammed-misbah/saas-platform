from pydantic import BaseModel


class CompanyCreate(BaseModel):
    company_name: str
    slug: str


class CompanyUpdate(BaseModel):
    company_name: str
    slug: str
    is_active: bool


class CompanyResponse(BaseModel):
    id: int
    company_name: str
    slug: str
    is_active: bool

    class Config:
        from_attributes = True