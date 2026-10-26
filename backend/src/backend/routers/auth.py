from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import SignUpRequest, SignInRequest, AuthResponse
from ..auth_utils import hash_password, verify_password

router = APIRouter(tags=["auth"])

@router.post("/signup", response_model=AuthResponse)
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )
    
    # Create new user with hashed password
    new_user = User(
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return AuthResponse(
        access_token=f"mock-jwt-token-{new_user.id}", # Replace with real JWT if needed
        user_name=new_user.name
    )


@router.post("/signin", response_model=AuthResponse)
def signin(request: SignInRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    return AuthResponse(
        access_token=f"mock-jwt-token-{user.id}",
        user_name=user.name
    )