from fastapi import FastAPI, Request
from app.db.session import engine
from sqlalchemy import text
from app.middleware.exception_handler import global_exception_handler
from app.core.logger import logger
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.companies import router as company_router
from app.api.projects import router as project_router
from app.api.assign_projects import router as assign_user_projects
from app.api.files import router as files_upload

from app.middleware.tenant_middleware import TenantMiddleware


logger.info("Application Started")

app = FastAPI()

app.add_exception_handler(Exception, global_exception_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request Received: {request.method} {request.url}")
    response = await call_next(request)
    return response

app.add_middleware(TenantMiddleware)


app.include_router(auth_router)

app.include_router(files_upload)

app.include_router(project_router)

app.include_router(assign_user_projects)

app.include_router(company_router)

app.include_router(users_router)
