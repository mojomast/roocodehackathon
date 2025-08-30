import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Define the base for declarative models
Base = declarative_base()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL - BE-001: Ensure it's not None or empty
if not DATABASE_URL or not DATABASE_URL.strip():
    raise ValueError("DATABASE_URL environment variable is required and cannot be empty")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    """
    Dependency function to get a database session.
    Yields a session and ensures proper cleanup even on failures.
    Handles errors to prevent session leaks and ensures transaction integrity.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Rollback on any exception to ensure clean state
        try:
            db.rollback()
        except Exception:
            pass  # Ignore rollback errors during cleanup
        raise e
    finally:
        # Always close the session to prevent connection pool exhaustion
        try:
            db.close()
        except Exception:
            pass  # Ignore close errors during cleanup

class User(Base):
    """
    SQLAlchemy model for a User.
    Represents a user with GitHub authentication details and optional email.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    access_token = Column(String)
    email = Column(String, nullable=True)  # BE-002: Added email field to User model

    repos = relationship("Repo", back_populates="owner")

class Repo(Base):
    """
    SQLAlchemy model for a Repository.
    Represents a repository linked by a user.
    """
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    repo_url = Column(String, index=True)
    repo_name = Column(String, index=True) # Added repo_name
    status = Column(String, default="connected") # e.g., "connected", "disconnected"

    owner = relationship("User", back_populates="repos")
    jobs = relationship("Job", back_populates="repository")

class Job(Base):
    """
    SQLAlchemy model for a Job.
    Represents a documentation generation job for a repository.
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"))
    status = Column(String, default="pending") # e.g., "pending", "running", "completed", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    repository = relationship("Repo", back_populates="jobs")