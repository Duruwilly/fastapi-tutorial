from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import Users
from database import SessionLocal
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# this is to add a signature to the jwt to make sure that the jwt is secured and autorized
SECRET_KEY = "04123666f8f70ccfe3cf3db061c2025e768db3d0fac95fbb3c4cabd0b50e1626"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #this is a password hashing context that will be used to hash and verify passwords. The bcrypt algorithm is a widely used and secure hashing algorithm that is designed to be slow, making it more resistant to brute-force attacks. The deprecated="auto" argument tells the context to automatically handle any deprecated algorithms and use the recommended ones instead.
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

class create_user_request(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, role: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "role": role, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError as e:
        print("JWT error:", repr(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: create_user_request):
    # Check if the user already exists
    existing_user = db.query(Users).filter_by(email=create_user_request.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    # Create a new user
    new_user = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),  # Hash the password before storing it
        role=create_user_request.role,
        is_active=True,
        phone_number=create_user_request.phone_number
    )
    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(username=new_user.username, role=new_user.role, user_id=new_user.id, expires_delta=timedelta(minutes=20))
    return {"message": "User created successfully", "token": token}

@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(username=form_data.username, role=user.role, user_id=user.id, expires_delta=timedelta(minutes=20))
    return {"message": "Login successful", "access_token": token, "token_type": "bearer"}