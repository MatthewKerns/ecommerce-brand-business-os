#!/usr/bin/env python3
"""
Database initialization script for AI Content Agents.

This script manages database initialization and migrations for the content agents system.
It supports both SQLAlchemy ORM-based initialization and SQL migration files.

Usage:
    python database/init_db.py                 # Initialize database
    python database/init_db.py --dry-run       # Show what would be done without executing
    python database/init_db.py --force         # Force recreation of tables (drops existing)
    python database/init_db.py --migrations    # Run SQL migrations from migrations/ directory

Examples:
    # Development setup
    python database/init_db.py

    # Check what will happen without making changes
    python database/init_db.py --dry-run

    # Reset database (WARNING: destroys data)
    python database/init_db.py --force
"""
import argparse
import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import engine, Base, DATABASE_URL
from database import models  # noqa: F401 - Import models to register them with Base
from analytics import models as analytics_models  # noqa: F401 - Import analytics models to register them with Base


def get_migration_files() -> List[Path]:
    """
    Get all migration files in order.

    Returns:
        List[Path]: Sorted list of migration SQL files
    """
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        return []

    migration_files = sorted(migrations_dir.glob("*.sql"))
    return migration_files


def run_sql_migration(migration_file: Path, dry_run: bool = False) -> bool:
    """
    Run a SQL migration file.

    Args:
        migration_file: Path to the SQL migration file
        dry_run: If True, only show what would be done

    Returns:
        bool: True if successful, False otherwise
    """
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"\n📄 Processing migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        sql_content = f.read()

    if dry_run:
        print(f"   [DRY RUN] Would execute {len(sql_content)} characters of SQL")
        print(f"   Preview (first 200 chars): {sql_content[:200]}...")
        return True

    try:
        # Execute the SQL file
        with engine.connect() as connection:
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            for i, statement in enumerate(statements, 1):
                if statement:
                    connection.execute(statement)
                    print(f"   ✓ Executed statement {i}/{len(statements)}")
            connection.commit()

        print(f"   ✅ Migration completed: {migration_file.name}")
        return True

    except Exception as e:
        print(f"   ❌ Migration failed: {e}")
        return False


def init_database_orm(dry_run: bool = False, force: bool = False) -> bool:
    """
    Initialize database using SQLAlchemy ORM models.

    Args:
        dry_run: If True, only show what would be done
        force: If True, drop existing tables before creating

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔧 Initializing database using SQLAlchemy ORM...")
    print(f"   Database URL: {DATABASE_URL}")

    if dry_run:
        print("   [DRY RUN] Would create the following tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"      - {table_name}")
        return True

    try:
        if force:
            print("   ⚠️  Dropping existing tables (--force flag set)...")
            Base.metadata.drop_all(bind=engine)
            print("   ✓ Existing tables dropped")

        print("   Creating tables...")
        Base.metadata.create_all(bind=engine)

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print("\n   ✅ Database initialized successfully!")
        print(f"   Created {len(tables)} tables:")
        for table in tables:
            print(f"      - {table}")

        return True

    except Exception as e:
        print(f"\n   ❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_database_migrations(dry_run: bool = False) -> bool:
    """
    Initialize database using SQL migration files.

    Args:
        dry_run: If True, only show what would be done

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔧 Initializing database using SQL migrations...")
    print(f"   Database URL: {DATABASE_URL}")

    migration_files = get_migration_files()

    if not migration_files:
        print("   ⚠️  No migration files found in migrations/ directory")
        return False

    print(f"   Found {len(migration_files)} migration file(s)")

    success = True
    for migration_file in migration_files:
        if not run_sql_migration(migration_file, dry_run):
            success = False
            break

    if success:
        print("\n   ✅ All migrations completed successfully!")
    else:
        print("\n   ❌ Migration process failed")

    return success


def verify_database() -> bool:
    """
    Verify database is properly initialized.

    Returns:
        bool: True if database is valid, False otherwise
    """
    print("\n🔍 Verifying database...")

    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            'content_history', 'api_usage', 'performance_metrics',
            'tiktok_channels', 'channel_content', 'scheduled_content', 'publish_log',
            'tiktok_metrics', 'website_analytics', 'email_metrics', 'sales_data'
        ]
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            print(f"   ❌ Missing tables: {', '.join(missing_tables)}")
            return False

        print(f"   ✓ Found all {len(expected_tables)} expected tables")

        # Verify each table has columns
        for table_name in expected_tables:
            columns = inspector.get_columns(table_name)
            print(f"   ✓ {table_name}: {len(columns)} columns")

        print("\n   ✅ Database verification passed!")
        return True

    except Exception as e:
        print(f"\n   ❌ Database verification failed: {e}")
        return False


def main():
    """Main entry point for database initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize AI Content Agents database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreation of tables (WARNING: destroys existing data)'
    )

    parser.add_argument(
        '--migrations',
        action='store_true',
        help='Use SQL migration files instead of ORM models'
    )

    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify database, do not initialize'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("AI CONTENT AGENTS - DATABASE INITIALIZATION")
    print("=" * 70)

    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")

    if args.force and not args.dry_run:
        print("\n⚠️  WARNING: --force flag will DELETE all existing data!")
        response = input("   Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("   Cancelled.")
            return 1

    # Verify only mode
    if args.verify_only:
        success = verify_database()
        return 0 if success else 1

    # Initialize database
    if args.migrations:
        success = init_database_migrations(dry_run=args.dry_run)
    else:
        success = init_database_orm(dry_run=args.dry_run, force=args.force)

    # Verify after initialization (unless dry run)
    if success and not args.dry_run:
        success = verify_database()

    print("\n" + "=" * 70)
    if success:
        print("✅ DATABASE INITIALIZATION COMPLETE")
    else:
        print("❌ DATABASE INITIALIZATION FAILED")
    print("=" * 70 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
