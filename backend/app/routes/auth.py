from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.utils.security import hash_password
from app.schemas.user import UserLogin
from app.utils.security import verify_password
from app.utils.jwt import create_access_token

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken."
        )

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if user.password != db_user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "user_id": db_user.user_id,
            "username": db_user.username
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user.user_id,
        "username": db_user.username
    }