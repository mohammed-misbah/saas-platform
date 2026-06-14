from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from jose import jwt, JWTError

from app.db.session import SessionLocal
from app.models.user import User
from app.core.config import settings


class TenantMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        request.state.current_user = None
        request.state.company_id = None

        try:

            authorization = request.headers.get("Authorization")

            if authorization and authorization.startswith("Bearer "):

                token = authorization.replace("Bearer ", "")

                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )

                email = payload.get("sub")

                if email:

                    db = SessionLocal()

                    try:

                        user = (
                            db.query(User)
                            .filter(User.email == email)
                            .first()
                        )

                        if user:

                            request.state.current_user = user
                            request.state.company_id = user.company_id

                    finally:
                        db.close()

        except JWTError:
            pass

        response = await call_next(request)

        return response