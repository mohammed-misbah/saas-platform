from fastapi import FastAPI
from app.db.session import engine
from sqlalchemy import text
from app.middleware.exception_handler import global_exception_handler
from app.core.logging import logger

logger.info("Application Started")

app = FastAPI()

app.add_exception_handler(Exception, global_exception_handler)

from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request Received: {request.method} {request.url}")
    response = await call_next(request)
    return response

@app.get("/test-error")
def test_error():
    raise Exception("Something went wrong")

@app.get("/health")
def health_check():
    return {"status": "healthy"}