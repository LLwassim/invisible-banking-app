from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
def signup(
    user_data: SignupRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """Create a new user account and return access token."""
    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
def login(
    user_data: LoginRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """Authenticate user and return access token."""
    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token)
