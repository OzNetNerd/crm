#!/usr/bin/env python3
"""
Clean up legacy entity columns from Task model after successful migration
"""

from main import create_app
from app.models import db


def cleanup_legacy_task_columns():
    """Remove legacy entity_type and entity_id columns from tasks table"""
    print("🧹 Cleaning up legacy task entity columns")

    app = create_app()

    with app.app_context():
        try:
            # SQLite doesn't support DROP COLUMN, so we'll create a new table and migrate
            print("🔄 Creating new tasks table without legacy columns")

            # Create new table structure
            db.session.execute(
                db.text(
                    """
                CREATE TABLE tasks_new (
                    id INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    due_date DATE,
                    priority VARCHAR(10) DEFAULT 'medium',
                    status VARCHAR(20) DEFAULT 'todo',
                    next_step_type VARCHAR(20),
                    created_at DATETIME,
                    completed_at DATETIME,
                    task_type VARCHAR(20) DEFAULT 'single',
                    parent_task_id INTEGER,
                    sequence_order INTEGER DEFAULT 0,
                    dependency_type VARCHAR(20) DEFAULT 'parallel',
                    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
                )
            """
                )
            )

            print("🔄 Migrating task data to new structure")

            # Copy data from old table to new table
            db.session.execute(
                db.text(
                    """
                INSERT INTO tasks_new (
                    id, description, due_date, priority, status, next_step_type,
                    created_at, completed_at, task_type, parent_task_id, 
                    sequence_order, dependency_type
                )
                SELECT 
                    id, description, due_date, priority, status, next_step_type,
                    created_at, completed_at, task_type, parent_task_id,
                    sequence_order, dependency_type
                FROM tasks
            """
                )
            )

            print("🔄 Replacing old tasks table")

            # Drop old table and rename new one
            db.session.execute(db.text("DROP TABLE tasks"))
            db.session.execute(db.text("ALTER TABLE tasks_new RENAME TO tasks"))

            db.session.commit()
            print("✅ Successfully cleaned up legacy task columns")
            return True

        except Exception as e:
            print(f"❌ Failed to clean up legacy columns: {e}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    if cleanup_legacy_task_columns():
        print("🎉 Legacy column cleanup completed successfully!")
    else:
        print("💥 Legacy column cleanup failed!")
