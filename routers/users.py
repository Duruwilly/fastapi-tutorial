from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import Users
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix="/users",
    tags=["users"],
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

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Permission denied")
    return db.query(Users).all() #this will query the database for all the users

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Permission denied")
    user_model = db.query(Users).filter(Users.id == user_id).first() #this will query the database for a specific user based on the id provided in the URL path parameter and return it as a User object
    if user_model is not None:
        db.delete(user_model) #this will delete the user from the database
        db.commit() #this will commit the changes to the database, saving the changes to the users table
        return {"detail": f"User deleted successfully"} #this will return a success message if the user is deleted successfully
    raise HTTPException(status_code=404, detail=f"User not found") #this will return a 404 error if the user is not found in the database