#!/usr/bin/env python3
"""
Database migration: Add review workflow and versioning support.

Migration: add_review_and_versioning
Description: Creates ContentReview table and adds versioning fields to ContentHistory
Version: 0.5.0
Date: 2024-02-27

This migration:
1. Creates content_reviews table for approval workflow
2. Adds versioning fields to content_history table:
   - version_number: Integer version counter (default 1)
   - parent_content_id: FK to parent content for versioning
   - is_draft: Boolean flag for draft content

Usage:
    python database/migrations/add_review_and_versioning.py
"""
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import engine


def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        table_name: Name of the table

    Returns:
        bool: True if table exists, False otherwise
    """
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return table_name in tables


def check_column_exists(table_name: str, column_name: str) -> bool:
    """
    Check if a column exists in a table.

    Args:
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        bool: True if column exists, False otherwise
    """
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def create_content_reviews_table() -> bool:
    """
    Create the content_reviews table for approval workflow.

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n📋 Creating content_reviews table...")

    # Check if table already exists
    if check_table_exists('content_reviews'):
        print("   ⏭️  Table 'content_reviews' already exists, skipping")
        return True

    try:
        with engine.connect() as connection:
            # Create content_reviews table
            sql = """
            CREATE TABLE content_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER NOT NULL,
                approval_status VARCHAR(20) NOT NULL DEFAULT 'draft',
                reviewer_id VARCHAR(50),
                review_notes TEXT,
                submitted_at DATETIME,
                reviewed_at DATETIME,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content_history (id) ON DELETE CASCADE,
                CHECK (approval_status IN ('draft', 'in_review', 'approved', 'rejected'))
            )
            """
            connection.execute(sql)
            connection.commit()

            print("   ✓ Created table: content_reviews")

            # Create indexes
            indexes = [
                ("idx_content_reviews_content_id", "content_id"),
                ("idx_content_reviews_approval_status", "approval_status"),
                ("idx_content_reviews_reviewer_id", "reviewer_id"),
                ("idx_content_reviews_submitted_at", "submitted_at"),
            ]

            for index_name, column_name in indexes:
                sql = f"CREATE INDEX {index_name} ON content_reviews ({column_name})"
                connection.execute(sql)
                connection.commit()
                print(f"   ✓ Created index: {index_name}")

            # Create composite index
            sql = "CREATE INDEX idx_content_reviews_status_submitted ON content_reviews (approval_status, submitted_at)"
            connection.execute(sql)
            connection.commit()
            print("   ✓ Created composite index: idx_content_reviews_status_submitted")

        print("\n   ✅ Successfully created content_reviews table with all indexes")
        return True

    except Exception as e:
        print(f"\n   ❌ Failed to create content_reviews table: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_versioning_fields() -> bool:
    """
    Add versioning fields to content_history table.

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔧 Adding versioning fields to content_history table...")

    # Define the fields to add
    versioning_fields = {
        'version_number': 'INTEGER DEFAULT 1',
        'parent_content_id': 'INTEGER',
        'is_draft': 'BOOLEAN DEFAULT 0'
    }

    try:
        # Check if table exists
        if not check_table_exists('content_history'):
            print("   ❌ Table 'content_history' does not exist")
            print("   Please run initial schema migration first")
            return False

        # Check which columns need to be added
        fields_to_add = []
        for field_name, field_type in versioning_fields.items():
            if not check_column_exists('content_history', field_name):
                fields_to_add.append((field_name, field_type))
            else:
                print(f"   ⏭️  Column '{field_name}' already exists, skipping")

        if not fields_to_add:
            print("\n   ✅ All versioning fields already exist, no migration needed")
            return True

        # Add the columns
        with engine.connect() as connection:
            for field_name, field_type in fields_to_add:
                print(f"   Adding column: {field_name} ({field_type})")

                # SQLite uses a simpler ALTER TABLE syntax
                sql = f"ALTER TABLE content_history ADD COLUMN {field_name} {field_type}"
                connection.execute(sql)
                connection.commit()

                print(f"   ✓ Added column: {field_name}")

            # Create foreign key index for parent_content_id if it was added
            if any(field[0] == 'parent_content_id' for field in fields_to_add):
                sql = "CREATE INDEX idx_content_history_parent_content_id ON content_history (parent_content_id)"
                connection.execute(sql)
                connection.commit()
                print("   ✓ Created index: idx_content_history_parent_content_id")

            # Create index for is_draft if it was added
            if any(field[0] == 'is_draft' for field in fields_to_add):
                sql = "CREATE INDEX idx_content_history_is_draft ON content_history (is_draft)"
                connection.execute(sql)
                connection.commit()
                print("   ✓ Created index: idx_content_history_is_draft")

        # Note: SQLite doesn't support adding foreign key constraints after table creation
        # The foreign key constraint for parent_content_id is enforced at the ORM level
        print("\n   ℹ️  Note: Foreign key constraint for parent_content_id is enforced at the ORM level")
        print("      - parent_content_id references content_history.id with ON DELETE SET NULL")

        print(f"\n   ✅ Migration completed successfully!")
        print(f"   Added {len(fields_to_add)} new column(s) to content_history")

        return True

    except Exception as e:
        print(f"\n   ❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_migration() -> bool:
    """
    Run the complete migration for review workflow and versioning.

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔧 Running migration: add_review_and_versioning")
    print("   Creating review workflow and versioning support...\n")

    # Step 1: Create content_reviews table
    reviews_success = create_content_reviews_table()
    if not reviews_success:
        print("\n   ❌ Failed to create content_reviews table")
        return False

    # Step 2: Add versioning fields to content_history
    versioning_success = add_versioning_fields()
    if not versioning_success:
        print("\n   ❌ Failed to add versioning fields")
        return False

    return True


def verify_migration() -> bool:
    """
    Verify that the migration was applied successfully.

    Returns:
        bool: True if verification passed, False otherwise
    """
    print("\n🔍 Verifying migration...")

    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)

        # Verify content_reviews table exists
        if 'content_reviews' not in inspector.get_table_names():
            print("   ❌ Table 'content_reviews' does not exist")
            return False

        print("   ✓ Table 'content_reviews' exists")

        # Verify content_reviews columns
        review_columns = [col['name'] for col in inspector.get_columns('content_reviews')]
        expected_review_columns = [
            'id', 'content_id', 'approval_status', 'reviewer_id', 'review_notes',
            'submitted_at', 'reviewed_at', 'created_at', 'updated_at'
        ]
        missing_review_columns = [col for col in expected_review_columns if col not in review_columns]

        if missing_review_columns:
            print(f"   ❌ Missing columns in content_reviews: {', '.join(missing_review_columns)}")
            return False

        print(f"   ✓ All {len(expected_review_columns)} content_reviews columns present")

        # Verify versioning columns in content_history
        history_columns = [col['name'] for col in inspector.get_columns('content_history')]
        expected_versioning_columns = ['version_number', 'parent_content_id', 'is_draft']
        missing_versioning_columns = [col for col in expected_versioning_columns if col not in history_columns]

        if missing_versioning_columns:
            print(f"   ❌ Missing versioning columns in content_history: {', '.join(missing_versioning_columns)}")
            return False

        print(f"   ✓ All {len(expected_versioning_columns)} versioning columns present in content_history")

        print("\n   ✅ Migration verification passed!")
        return True

    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def main():
    """Main entry point for the migration script."""
    print("=" * 70)
    print("Database Migration: Add Review Workflow and Versioning")
    print("=" * 70)

    # Run the migration
    success = run_migration()

    if not success:
        print("\n❌ Migration failed")
        sys.exit(1)

    # Verify the migration
    verified = verify_migration()

    if not verified:
        print("\n⚠️  Migration applied but verification failed")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ Migration completed and verified successfully!")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
