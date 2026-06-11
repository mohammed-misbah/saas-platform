from fastapi import APIRouter, Depends

from app.models.user import User
from app.db.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def current_user(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active
    }