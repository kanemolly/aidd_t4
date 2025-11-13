#!/usr/bin/env python
"""
Migration script: Add booking modification tracking fields.
Adds modified_by_id, modified_at, and change_summary columns to bookings table.
"""

import sqlite3
import os
from datetime import datetime

def add_modification_fields():
    """Add modification tracking columns to bookings table."""
    
    # Paths to database files
    db_paths = [
        os.path.join(os.path.dirname(__file__), 'instance', 'campus_hub.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'app.db'),
    ]
    
    # Columns to add
    columns = [
        ('modified_by_id', 'INTEGER'),
        ('modified_at', 'DATETIME'),
        ('change_summary', 'TEXT'),
    ]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            print(f"Database not found: {db_path}")
            continue
        
        print(f"\nProcessing: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(bookings)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            print(f"Existing columns: {existing_columns}")
            
            # Add columns if they don't exist
            for col_name, col_type in columns:
                if col_name not in existing_columns:
                    print(f"  Adding column: {col_name} ({col_type})")
                    cursor.execute(f"ALTER TABLE bookings ADD COLUMN {col_name} {col_type}")
                else:
                    print(f"  Column already exists: {col_name}")
            
            conn.commit()
            conn.close()
            print(f"✓ Successfully migrated: {db_path}")
            
        except sqlite3.Error as e:
            print(f"✗ Error migrating {db_path}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")

if __name__ == '__main__':
    add_modification_fields()
    print("\nMigration complete!")
