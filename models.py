from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) #this is the primary key for the table and will be used to uniquely identify each user
    email = Column(String, unique=True, index=True) #this is the email of the user and the index allows for faster searches based on the email. The unique constraint ensures that no two users can have the same email
    username = Column(String, unique=True, index=True) #this is the username of the user and the index allows for faster searches based on the username. The unique constraint ensures that no two users can have the same username
    first_name = Column(String) #this is the first name of the user
    last_name = Column(String) #this is the last name of the user
    hashed_password = Column(String) #this is the hashed password of the user
    is_active = Column(Boolean, default=True) #this indicates whether the user is active or not, with a default value of True
    role = Column(String, default="user") #this is the role of the user, with a default value of "user". This can be used to differentiate between different types of users (eg; admin, moderator, etc.)

class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True) #this is the primary key for the table and will be used to uniquely identify each todo item
    title = Column(String, index=True) #this is the title of the todo item and the index allows for faster searches based on the title
    description = Column(String) #this is the description of the todo item
    priority = Column(Integer) #this is the priority of the todo item
    completed = Column(Boolean, default=False) #this indicates whether the todo item has been completed or not, with a default value of False
    owner_id = Column(Integer, ForeignKey("users.id")) #this is a foreign key that references the id of the user who owns the todo item. This establishes a relationship between the todos table and the users table, allowing us to associate each todo item with a specific user