#!/usr/bin/env python3
"""
CRM Schema Migration Script
Handles database schema changes using reusable migration patterns
"""

from main import create_app
from app.models import db


class MigrationHelper:
    """Reusable migration utility following DRY principles"""

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

    def add_columns(self, table_name, columns):
        """Add multiple columns to a table"""
        success = True
        for column_def in columns:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_def}"
            if not self.execute_sql(sql, f"Adding column {column_def} to {table_name}"):
                success = False
        return success

    def create_table(self, table_name, table_def):
        """Create a new table"""
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({table_def})"
        return self.execute_sql(sql, f"Creating table {table_name}")

    def table_exists(self, table_name):
        """Check if a table exists"""
        with self.app.app_context():
            result = db.session.execute(
                db.text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"
                ),
                {"table_name": table_name},
            ).fetchone()
            return result is not None

    def column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        with self.app.app_context():
            result = db.session.execute(
                db.text(f"PRAGMA table_info({table_name})")
            ).fetchall()
            return any(row[1] == column_name for row in result)


def migrate_contact_opportunities_table(migration_helper):
    """Phase 1: Add stakeholder management columns to contact_opportunities"""
    print(
        "\n📋 Phase 1: Enhancing contact_opportunities table for stakeholder management"
    )

    columns_to_add = []

    # Check and add role column
    if not migration_helper.column_exists("contact_opportunities", "role"):
        columns_to_add.append("role VARCHAR(50)")
    else:
        print("ℹ️  Column 'role' already exists in contact_opportunities")

    # Check and add is_primary column
    if not migration_helper.column_exists("contact_opportunities", "is_primary"):
        columns_to_add.append("is_primary BOOLEAN DEFAULT FALSE")
    else:
        print("ℹ️  Column 'is_primary' already exists in contact_opportunities")

    if columns_to_add:
        return migration_helper.add_columns("contact_opportunities", columns_to_add)
    else:
        print("✅ contact_opportunities table already has required columns")
        return True


def migrate_legacy_tasks(migration_helper):
    """Phase 2: Migrate legacy task entity relationships"""
    print("\n📋 Phase 2: Migrating legacy task entity relationships")

    # Check if there are any legacy tasks to migrate
    with migration_helper.app.app_context():
        legacy_tasks = db.session.execute(
            db.text(
                """
            SELECT id, entity_type, entity_id 
            FROM tasks 
            WHERE entity_type IS NOT NULL 
            AND entity_id IS NOT NULL
            AND id NOT IN (
                SELECT DISTINCT task_id 
                FROM task_entities
            )
        """
            )
        ).fetchall()

        if not legacy_tasks:
            print("✅ No legacy tasks need migration")
            return True

        print(f"📊 Found {len(legacy_tasks)} legacy tasks to migrate")

        # Migrate each legacy task
        migrated_count = 0
        for task_id, entity_type, entity_id in legacy_tasks:
            try:
                db.session.execute(
                    db.text(
                        """
                    INSERT INTO task_entities (task_id, entity_type, entity_id, created_at)
                    VALUES (:task_id, :entity_type, :entity_id, datetime('now'))
                """
                    ),
                    {
                        "task_id": task_id,
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                    },
                )
                migrated_count += 1
            except Exception as e:
                print(f"❌ Failed to migrate task {task_id}: {e}")

        db.session.commit()
        print(f"✅ Migrated {migrated_count} legacy tasks to task_entities table")
        return migrated_count == len(legacy_tasks)


def create_team_tables(migration_helper):
    """Phase 3: Create team management tables"""
    print("\n📋 Phase 3: Creating team management tables")

    tables = {
        "users": """
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            role VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        """,
        "company_teams": """
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR(50) NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            access_level VARCHAR(20) DEFAULT 'read',
            assigned_date DATE DEFAULT CURRENT_DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(company_id, user_id, role)
        """,
        "opportunity_teams": """
            id INTEGER PRIMARY KEY,
            opportunity_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR(50) NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            access_level VARCHAR(20) DEFAULT 'read',
            assigned_date DATE DEFAULT CURRENT_DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(opportunity_id, user_id, role)
        """,
        "task_teams": """
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR(50) NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            access_level VARCHAR(20) DEFAULT 'read',
            assigned_date DATE DEFAULT CURRENT_DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(task_id, user_id, role)
        """,
    }

    success = True
    for table_name, table_def in tables.items():
        if not migration_helper.table_exists(table_name):
            if not migration_helper.create_table(table_name, table_def):
                success = False
        else:
            print(f"ℹ️  Table '{table_name}' already exists")

    return success


def main():
    """Main migration runner"""
    print("🚀 Starting CRM Schema Migration")

    app = create_app()
    migration_helper = MigrationHelper(app)

    # Run migration phases
    phases = [
        ("Contact Opportunities Enhancement", migrate_contact_opportunities_table),
        ("Legacy Task Migration", migrate_legacy_tasks),
        ("Team Tables Creation", create_team_tables),
    ]

    for phase_name, phase_func in phases:
        print(f"\n{'='*60}")
        print(f"Starting: {phase_name}")
        print("=" * 60)

        if not phase_func(migration_helper):
            print(f"❌ Migration phase '{phase_name}' failed!")
            return False

        print(f"✅ Migration phase '{phase_name}' completed successfully!")

    print(f"\n{'='*60}")
    print("🎉 All migration phases completed successfully!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    main()
