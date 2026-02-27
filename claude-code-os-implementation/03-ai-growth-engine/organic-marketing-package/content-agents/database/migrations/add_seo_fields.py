#!/usr/bin/env python3
"""
Database migration: Add SEO fields to content_history table.

Migration: add_seo_fields
Description: Adds SEO-related fields to content_history table for SEO optimization tracking
Version: 0.4.0
Date: 2024-02-26

This migration adds the following fields to content_history:
- seo_score: Numeric SEO score (0-100)
- seo_grade: Letter grade for SEO quality (A, B, C, D, F)
- target_keyword: Primary target keyword for SEO
- meta_description: SEO meta description (max 160 chars)
- internal_links: JSON array of internal linking suggestions

Usage:
    python database/migrations/add_seo_fields.py
"""
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import engine


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


def run_migration() -> bool:
    """
    Run the migration to add SEO fields to content_history table.

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔧 Running migration: add_seo_fields")
    print("   Adding SEO fields to content_history table...\n")

    # Define the fields to add
    seo_fields = {
        'seo_score': 'DECIMAL(5, 2)',
        'seo_grade': 'VARCHAR(1)',
        'target_keyword': 'VARCHAR(200)',
        'meta_description': 'VARCHAR(160)',
        'internal_links': 'TEXT'
    }

    try:
        # Check if table exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'content_history' not in tables:
            print("   ❌ Table 'content_history' does not exist")
            print("   Please run initial schema migration first")
            return False

        # Check which columns need to be added
        fields_to_add = []
        for field_name, field_type in seo_fields.items():
            if not check_column_exists('content_history', field_name):
                fields_to_add.append((field_name, field_type))
            else:
                print(f"   ⏭️  Column '{field_name}' already exists, skipping")

        if not fields_to_add:
            print("\n   ✅ All SEO fields already exist, no migration needed")
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

        # Note: SQLite doesn't support adding CHECK constraints after table creation
        # These constraints are defined in the ORM model and will be enforced there
        print("\n   ℹ️  Note: CHECK constraints are enforced at the ORM level")
        print("      - seo_score: 0-100")
        print("      - seo_grade: A, B, C, D, or F")

        print("\n   ✅ Migration completed successfully!")
        print(f"   Added {len(fields_to_add)} new column(s) to content_history")

        return True

    except Exception as e:
        print(f"\n   ❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


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
        columns = [col['name'] for col in inspector.get_columns('content_history')]

        expected_columns = ['seo_score', 'seo_grade', 'target_keyword', 'meta_description', 'internal_links']
        missing_columns = [col for col in expected_columns if col not in columns]

        if missing_columns:
            print(f"   ❌ Missing columns: {', '.join(missing_columns)}")
            return False

        print(f"   ✓ All {len(expected_columns)} SEO columns present")
        print("\n   ✅ Migration verification passed!")
        return True

    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def main():
    """Main entry point for the migration script."""
    print("=" * 70)
    print("Database Migration: Add SEO Fields")
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
