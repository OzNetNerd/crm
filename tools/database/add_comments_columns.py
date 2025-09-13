#!/usr/bin/env python3
"""
CRM Comments Migration Script
Adds comments columns to entities for simplified modals
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.crm.main import create_app
from app.models import db


class CommentsMigration:
    """Migration to add comments columns to all entity tables"""

    def __init__(self, app):
        self.app = app

    def execute_sql(self, sql, description):
        """Execute SQL with error handling and logging"""
        print(f"🔄 {description}")
        try:
            with self.app.app_context():
                db.session.execute(db.text(sql))
                db.session.commit()
            print(f"✅ {description} - SUCCESS")
            return True
        except Exception as e:
            print(f"❌ {description} - FAILED: {e}")
            return False

    def column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        with self.app.app_context():
            result = db.session.execute(
                db.text(f"PRAGMA table_info({table_name})")
            ).fetchall()
            return any(row[1] == column_name for row in result)

    def add_comments_column(self, table_name):
        """Add comments column to a table if it doesn't exist"""
        if self.column_exists(table_name, "comments"):
            print(f"ℹ️  Column 'comments' already exists in {table_name}")
            return True

        sql = f"ALTER TABLE {table_name} ADD COLUMN comments TEXT"
        return self.execute_sql(sql, f"Adding comments column to {table_name}")

    def run_migration(self):
        """Run the complete comments migration"""
        print("🚀 Adding comments columns to entity tables")

        # Tables that need comments columns
        tables = [
            "companies",
            "tasks",
            "stakeholders",
            "opportunities"
        ]

        success = True
        for table in tables:
            if not self.add_comments_column(table):
                success = False

        if success:
            print("\n✅ All comments columns added successfully!")
        else:
            print("\n❌ Some migrations failed!")

        return success


def main():
    """Main migration runner"""
    print("🚀 Starting Comments Column Migration")

    app = create_app()
    migration = CommentsMigration(app)

    success = migration.run_migration()

    if success:
        print("🎉 Migration completed successfully!")
        return True
    else:
        print("💥 Migration failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)