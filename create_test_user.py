from backend.models import Base, engine, User
from sqlalchemy.orm import sessionmaker

# Create test database engine and session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_user():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.access_token == "test-e2e-token").first()
        if existing_user:
            print(f"Test user already exists: {existing_user.username}")
            return existing_user

        # Create test user
        test_user = User(
            github_id="gh_test_001",
            username="testuser",
            access_token="test-e2e-token",
            email="test@example.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Created test user: {test_user.username} with token: {test_user.access_token}")
        return test_user
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()