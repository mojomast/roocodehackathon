#!/usr/bin/env python3
"""
Migration script to unify Job schema across backend and worker.

This script adds new columns to the Job table to support:
- clone_path: Path for repository cloning
- progress: Progress percentage (0-100)
- error_message: Error details for failed jobs
- retry_count: Number of retry attempts

Usage: python migrate.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Construct the path to the .env file relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

def run_migration():
    # Use the same DATABASE_URL as in models.py
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Add new columns to jobs table
        # Note: Using CHECK constraint for progress not enforced in SQLite, but ok for PostgreSQL

        print("Executing migration: Adding 'clone_path' column...")
        conn.execute(text("""
            ALTER TABLE jobs ADD COLUMN IF NOT EXISTS clone_path VARCHAR(500);
        """))
        conn.commit()
        print("'clone_path' column added or already exists.")
 
        print("Executing migration: Adding 'progress' column...")
        conn.execute(text("""
            ALTER TABLE jobs ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0;
        """))
        conn.commit()
        print("'progress' column added or already exists.")
 
        print("Executing migration: Adding 'error_message' column...")
        conn.execute(text("""
            ALTER TABLE jobs ADD COLUMN IF NOT EXISTS error_message TEXT;
        """))
        conn.commit()
        print("'error_message' column added or already exists.")
 
        print("Executing migration: Adding 'retry_count' column...")
        conn.execute(text("""
            ALTER TABLE jobs ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;
        """))
        conn.commit()
        print("'retry_count' column added or already exists.")
 
        print("Executing migration: Adding 'provider' column...")
        conn.execute(text("""
            ALTER TABLE jobs ADD COLUMN IF NOT EXISTS provider VARCHAR(255) DEFAULT 'openai';
        """))
        conn.commit()
        print("'provider' column added or already exists.")
 
        print("Executing migration: Adding 'model_name' column...")
        conn.execute(text("""
            ALTER TABLE jobs ADD COLUMN IF NOT EXISTS model_name VARCHAR(255) DEFAULT 'gpt-4-turbo';
        """))
        conn.commit()
        print("'model_name' column added or already exists.")
 
        # Update existing records to have default progress if needed
        conn.execute(text("""
            UPDATE jobs SET progress = 0 WHERE progress IS NULL;
        """))
        conn.commit()

        conn.execute(text("""
            UPDATE jobs SET retry_count = 0 WHERE retry_count IS NULL;
        """))
        conn.commit()

        # For PostgreSQL, this might be needed, but in SQLite it's fine
        # conn.commit() if using raw conn

        print("Migration completed successfully: Added clone_path, progress, error_message, retry_count columns to jobs table.")

if __name__ == "__main__":
    run_migration()