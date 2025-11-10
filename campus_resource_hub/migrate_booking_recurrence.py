"""
Migration script to add recurrence and approval fields to bookings table.
Run this once to update existing database schema.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from src.extensions import db

app = create_app()

with app.app_context():
    try:
        # Add new columns to bookings table
        with db.engine.connect() as conn:
            # Check if columns exist first
            result = conn.execute(db.text("PRAGMA table_info(bookings)")).fetchall()
            existing_columns = [row[1] for row in result]
            
            print("Existing columns:", existing_columns)
            
            # Add recurrence fields
            if 'is_recurring' not in existing_columns:
                print("Adding is_recurring column...")
                conn.execute(db.text("ALTER TABLE bookings ADD COLUMN is_recurring BOOLEAN DEFAULT 0"))
                conn.commit()
                print("✓ Added is_recurring")
            
            if 'recurrence_pattern' not in existing_columns:
                print("Adding recurrence_pattern column...")
                conn.execute(db.text("ALTER TABLE bookings ADD COLUMN recurrence_pattern VARCHAR(20)"))
                conn.commit()
                print("✓ Added recurrence_pattern")
            
            if 'recurrence_end_date' not in existing_columns:
                print("Adding recurrence_end_date column...")
                conn.execute(db.text("ALTER TABLE bookings ADD COLUMN recurrence_end_date DATETIME"))
                conn.commit()
                print("✓ Added recurrence_end_date")
            
            if 'parent_booking_id' not in existing_columns:
                print("Adding parent_booking_id column...")
                conn.execute(db.text("ALTER TABLE bookings ADD COLUMN parent_booking_id INTEGER"))
                conn.commit()
                print("✓ Added parent_booking_id")
            
            # Add approval tracking fields
            if 'approved_by_id' not in existing_columns:
                print("Adding approved_by_id column...")
                conn.execute(db.text("ALTER TABLE bookings ADD COLUMN approved_by_id INTEGER"))
                conn.commit()
                print("✓ Added approved_by_id")
            
            if 'approved_at' not in existing_columns:
                print("Adding approved_at column...")
                conn.execute(db.text("ALTER TABLE bookings ADD COLUMN approved_at DATETIME"))
                conn.commit()
                print("✓ Added approved_at")
            
            print("\n✅ Migration completed successfully!")
            print("All new fields added to bookings table.")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
