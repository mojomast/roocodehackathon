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
from sqlalchemy import create_engine

def run_migration():
    # Use the same DATABASE_URL as in models.py
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Add new columns to jobs table
        # Note: Using CHECK constraint for progress not enforced in SQLite, but ok for PostgreSQL

        conn.execute("""
            ALTER TABLE jobs ADD COLUMN clone_path VARCHAR(500);
        """)

        conn.execute("""
            ALTER TABLE jobs ADD COLUMN progress INTEGER DEFAULT 0;
        """)

        conn.execute("""
            ALTER TABLE jobs ADD COLUMN error_message TEXT;
        """)

        conn.execute("""
            ALTER TABLE jobs ADD COLUMN retry_count INTEGER DEFAULT 0;
        """)

        # Update existing records to have default progress if needed
        conn.execute("""
            UPDATE jobs SET progress = 0 WHERE progress IS NULL;
        """)

        conn.execute("""
            UPDATE jobs SET retry_count = 0 WHERE retry_count IS NULL;
        """)

        # For PostgreSQL, this might be needed, but in SQLite it's fine
        # conn.commit() if using raw conn

        print("Migration completed successfully: Added clone_path, progress, error_message, retry_count columns to jobs table.")

if __name__ == "__main__":
    run_migration()