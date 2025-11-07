"""
Database migration script to add user preference fields
Run this to update the database schema without losing data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extensions import db
from app import create_app

def migrate_user_preferences():
    """Add new preference fields to users table."""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration for user preferences...")
        
        # Check if columns already exist
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        new_columns = {
            'year_in_school': 'VARCHAR(20)',
            'major': 'VARCHAR(120)',
            'interests': 'TEXT',
            'study_preferences': 'TEXT',
            'accessibility_needs': 'TEXT',
            'preferred_locations': 'TEXT'
        }
        
        columns_to_add = []
        for col_name, col_type in new_columns.items():
            if col_name not in existing_columns:
                columns_to_add.append((col_name, col_type))
        
        if not columns_to_add:
            print("✅ All columns already exist. No migration needed.")
            return
        
        print(f"📝 Adding {len(columns_to_add)} new columns...")
        
        # Add each missing column
        for col_name, col_type in columns_to_add:
            try:
                sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"
                db.session.execute(db.text(sql))
                db.session.commit()
                print(f"  ✓ Added column: {col_name}")
            except Exception as e:
                print(f"  ⚠️  Error adding {col_name}: {e}")
                db.session.rollback()
        
        print("✅ Migration completed successfully!")
        
        # Verify
        inspector = db.inspect(db.engine)
        final_columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"\n📊 User table now has {len(final_columns)} columns:")
        for col in sorted(final_columns):
            print(f"  • {col}")


if __name__ == '__main__':
    migrate_user_preferences()
