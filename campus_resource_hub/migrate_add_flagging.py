"""
Migration script to add flagging columns to reviews table
Run this once to update the database schema
"""

from app import create_app
from src.extensions import db

def migrate():
    app = create_app()
    
    with app.app_context():
        # Add new columns using raw SQL
        try:
            # Check if columns already exist
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('reviews')]
            
            with db.engine.connect() as conn:
                if 'is_flagged' not in columns:
                    conn.execute(text('ALTER TABLE reviews ADD COLUMN is_flagged BOOLEAN DEFAULT 0 NOT NULL'))
                    conn.commit()
                    print("✓ Added is_flagged column")
                else:
                    print("○ is_flagged column already exists")
                    
                if 'flag_count' not in columns:
                    conn.execute(text('ALTER TABLE reviews ADD COLUMN flag_count INTEGER DEFAULT 0 NOT NULL'))
                    conn.commit()
                    print("✓ Added flag_count column")
                else:
                    print("○ flag_count column already exists")
                    
                if 'flag_reason' not in columns:
                    conn.execute(text('ALTER TABLE reviews ADD COLUMN flag_reason TEXT'))
                    conn.commit()
                    print("✓ Added flag_reason column")
                else:
                    print("○ flag_reason column already exists")
                    
                if 'flagged_by' not in columns:
                    conn.execute(text('ALTER TABLE reviews ADD COLUMN flagged_by TEXT'))
                    conn.commit()
                    print("✓ Added flagged_by column")
                else:
                    print("○ flagged_by column already exists")
                    
                if 'flagged_at' not in columns:
                    conn.execute(text('ALTER TABLE reviews ADD COLUMN flagged_at DATETIME'))
                    conn.commit()
                    print("✓ Added flagged_at column")
                else:
                    print("○ flagged_at column already exists")
                
                # Add index
                try:
                    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_reviews_is_flagged ON reviews (is_flagged)'))
                    conn.commit()
                    print("✓ Added index on is_flagged")
                except:
                    print("○ Index already exists or not needed")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate()
