from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() #this is the base class for all our database models. Any model we create will inherit from this class

SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db" #our database is going to be inside our directory of the todo app, and the name of the database is going to be todos.db

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} #this is a special argument that is required only for SQLite. It tells the SQLAlchemy engine to allow connections from multiple threads. SQLite has a limitation that it can only be accessed by the thread that created it
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #this is saying that the session local object will not automatically commit changes to the database and will not automatically flush changes to the database which gives us more control over when changes are persisted. The session will be bound to the engine we created above