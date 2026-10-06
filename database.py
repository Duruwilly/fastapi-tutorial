from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() #this is the base class for all our database models. Any model we create will inherit from this class

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:test1234@localhost/TodoApplicationDatabase" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL #this is the database engine that will be used to connect to the database. It will be used to create a new database session and execute SQL queries against the database
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #this is saying that the session local object will not automatically commit changes to the database and will not automatically flush changes to the database which gives us more control over when changes are persisted. The session will be bound to the engine we created above