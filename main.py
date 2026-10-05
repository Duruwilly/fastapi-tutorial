from fastapi import FastAPI
import models
from database import engine
from routers import auth, profile, todos, admin, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine) #this will create everything from the database.py file and models.py file to be able to create a new database that has a new table of todos with the structure defined in the Todo model
#and as a side note, this will only run the first time the application is started, creating the necessary tables in the database(eg; todos.db) if they do not already exist

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(profile.router)
app.include_router(users.router)