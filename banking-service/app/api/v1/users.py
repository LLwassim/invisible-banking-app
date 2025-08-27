from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserOut:
    """Get current user information."""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name
    )
