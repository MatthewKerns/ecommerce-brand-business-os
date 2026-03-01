#!/usr/bin/env python3
"""
Database migration: Add Klaviyo integration models.

This migration adds three new tables for Klaviyo integration:
- klaviyo_profiles: Customer profiles synced from Klaviyo
- klaviyo_sync_history: Synchronization operation tracking
- klaviyo_segments: Customer segmentation data

Usage:
    python database/migrations/add_klaviyo_models.py         # Apply migration
    python database/migrations/add_klaviyo_models.py --dry-run  # Preview changes

Migration: 002_add_klaviyo_models
Date: 2024-01-01
Dependencies: 001_initial_schema
"""
import argparse
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import engine, Base
from database.models import KlaviyoProfile, KlaviyoSyncHistory, KlaviyoSegment  # noqa: F401


def apply_migration(dry_run: bool = False) -> bool:
    """
    Apply the Klaviyo models migration.

    Args:
        dry_run: If True, only show what would be done without executing

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔄 Migration: add_klaviyo_models")
    print("=" * 70)
    print("Description: Add Klaviyo integration tables for customer profiles,")
    print("             sync history, and segmentation")
    print("=" * 70)

    tables_to_create = [
        ('klaviyo_profiles', 'Customer profiles synced from Klaviyo'),
        ('klaviyo_sync_history', 'Synchronization operation tracking'),
        ('klaviyo_segments', 'Customer segmentation data'),
    ]

    if dry_run:
        print("\n[DRY RUN] Would create the following tables:")
        for table_name, description in tables_to_create:
            print(f"   📋 {table_name}")
            print(f"      {description}")
        print("\n✓ Dry run completed - no changes made")
        return True

    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Check which tables need to be created
        tables_needed = []
        for table_name, description in tables_to_create:
            if table_name not in existing_tables:
                tables_needed.append((table_name, description))

        if not tables_needed:
            print("\n✓ All Klaviyo tables already exist - migration already applied")
            return True

        print(f"\n📝 Creating {len(tables_needed)} new table(s)...")

        # Create only the Klaviyo tables
        # We use Base.metadata.create_all which is idempotent (safe to run multiple times)
        # It will only create tables that don't exist
        Base.metadata.create_all(
            bind=engine,
            tables=[
                KlaviyoProfile.__table__,
                KlaviyoSyncHistory.__table__,
                KlaviyoSegment.__table__,
            ]
        )

        # Verify tables were created
        inspector = inspect(engine)
        tables_after = inspector.get_table_names()

        for table_name, description in tables_needed:
            if table_name in tables_after:
                print(f"   ✅ Created: {table_name}")
                print(f"      {description}")
            else:
                print(f"   ❌ Failed to create: {table_name}")
                return False

        print("\n" + "=" * 70)
        print("✅ Migration completed successfully!")
        print("=" * 70)

        # Show table details
        print("\n📊 Table Details:")
        for table_name, _ in tables_needed:
            if table_name in tables_after:
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                print(f"\n   {table_name}:")
                print(f"      Columns: {len(columns)}")
                print(f"      Indexes: {len(indexes)}")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def rollback_migration(dry_run: bool = False) -> bool:
    """
    Rollback the Klaviyo models migration.

    Args:
        dry_run: If True, only show what would be done without executing

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n⚠️  Rolling back migration: add_klaviyo_models")
    print("=" * 70)

    tables_to_drop = ['klaviyo_segments', 'klaviyo_sync_history', 'klaviyo_profiles']

    if dry_run:
        print("\n[DRY RUN] Would drop the following tables:")
        for table_name in tables_to_drop:
            print(f"   ❌ {table_name}")
        print("\n✓ Dry run completed - no changes made")
        return True

    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        tables_to_actually_drop = [t for t in tables_to_drop if t in existing_tables]

        if not tables_to_actually_drop:
            print("\n✓ No Klaviyo tables found - nothing to rollback")
            return True

        print(f"\n⚠️  Dropping {len(tables_to_actually_drop)} table(s)...")
        print("   This will DELETE ALL DATA in these tables!")

        # Drop tables in reverse order to handle foreign key constraints
        Base.metadata.drop_all(
            bind=engine,
            tables=[
                KlaviyoSegment.__table__,
                KlaviyoSyncHistory.__table__,
                KlaviyoProfile.__table__,
            ]
        )

        # Verify tables were dropped
        inspector = inspect(engine)
        tables_after = inspector.get_table_names()

        for table_name in tables_to_actually_drop:
            if table_name not in tables_after:
                print(f"   ✅ Dropped: {table_name}")
            else:
                print(f"   ❌ Failed to drop: {table_name}")
                return False

        print("\n" + "=" * 70)
        print("✅ Rollback completed successfully!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Rollback failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Add Klaviyo integration models to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Apply migration
    python database/migrations/add_klaviyo_models.py

    # Preview changes
    python database/migrations/add_klaviyo_models.py --dry-run

    # Rollback migration (WARNING: destroys data!)
    python database/migrations/add_klaviyo_models.py --rollback

    # Preview rollback
    python database/migrations/add_klaviyo_models.py --rollback --dry-run
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback this migration (WARNING: destroys data!)'
    )

    args = parser.parse_args()

    if args.rollback:
        success = rollback_migration(dry_run=args.dry_run)
    else:
        success = apply_migration(dry_run=args.dry_run)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
