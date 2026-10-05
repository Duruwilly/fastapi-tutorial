from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import Users
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix="/me",
    tags=["me"],
)

# Dependency to get the database session for each request
# This function will be used as a dependency in the route handlers to get a database session for each request
# It will automatically handle opening and closing the database session for each request.
# the yield statement will return or provide the database session to the route handler and then close it after the request is completed. So only the code prior to the yield statement will be executed before the request is handled and sending a response back to the client.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() #this will close the database session after the request is completed

#Depends is a special function provided by FastAPI that allows us to declare dependencies for our route handlers. In this case, we are using it to declare that the read_all function depends on the get_db function to provide a database session for each request.
#Basically means, it allows us to do something before executing what we to execute in the function, and then inject the dependency that the function relies on. In this case, it allows us to get a database session before executing the read_all function and then close the database session after executing the read_all function.
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)] #this is a dependency that will be used to get the current user from the JWT token provided in the request header. It will automatically handle decoding the JWT token and extracting the user information from it. The user information will be provided as a dictionary to the route handler.

class PasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, description="The new password for the user", example="newpassword123")
    # confirm_password: str = Field(min_length=8, description="The confirmation of the new password for the user", example="newpassword123")

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_profile = db.query(Users).filter(Users.id == user.get("id")).first()
    return {"first_name": user_profile.first_name, "last_name": user_profile.last_name, "email": user_profile.email, "username": user_profile.username, "role": user_profile.role, "is_active": user_profile.is_active}

@router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, password_request: PasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_profile = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_profile is None:
        raise HTTPException(status_code=404, detail=f"User not found")
    # if password_request.new_password != password_request.confirm_password:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if not bcrypt_context.verify(password_request.current_password, user_profile.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    user_profile.hashed_password = bcrypt_context.hash(password_request.new_password)
    db.add(user_profile)
    db.commit()
    return {"message": "Password changed successfully"}