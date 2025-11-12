"""Add cancellation tracking fields to bookings table"""
from src.extensions import db
from app import create_app

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Try to add the columns if they don't exist
            with db.engine.connect() as conn:
                try:
                    conn.execute(db.text('ALTER TABLE bookings ADD COLUMN cancellation_reason TEXT'))
                    print('✅ Added cancellation_reason column')
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print('⚠️  cancellation_reason column already exists')
                    else:
                        print(f'❌ Error adding cancellation_reason: {e}')
                
                try:
                    conn.execute(db.text('ALTER TABLE bookings ADD COLUMN cancelled_by_id INTEGER'))
                    print('✅ Added cancelled_by_id column')
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print('⚠️  cancelled_by_id column already exists')
                    else:
                        print(f'❌ Error adding cancelled_by_id: {e}')
                
                conn.commit()
            
            print('\n✅ Migration completed successfully!')
        except Exception as e:
            print(f'❌ Migration failed: {e}')

if __name__ == '__main__':
    migrate()
