"""Migrate all database files"""
import sqlite3
import os

def migrate_db(db_path):
    if not os.path.exists(db_path):
        print(f'Database not found: {db_path}')
        return
    
    print(f'\nMigrating: {db_path}')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute('PRAGMA table_info(bookings)')
    columns = [col[1] for col in cursor.fetchall()]
    
    has_cancellation = 'cancellation_reason' in columns
    has_cancelled_by = 'cancelled_by_id' in columns
    
    print(f'  - has cancellation_reason: {has_cancellation}')
    print(f'  - has cancelled_by_id: {has_cancelled_by}')
    
    # Add missing columns
    if not has_cancellation:
        cursor.execute('ALTER TABLE bookings ADD COLUMN cancellation_reason TEXT')
        print('  [+] Added cancellation_reason')
    
    if not has_cancelled_by:
        cursor.execute('ALTER TABLE bookings ADD COLUMN cancelled_by_id INTEGER')
        print('  [+] Added cancelled_by_id')
    
    conn.commit()
    conn.close()
    print(f'  Done!')

if __name__ == '__main__':
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    
    # Migrate both databases
    migrate_db(os.path.join(instance_path, 'campus_hub.db'))
    migrate_db(os.path.join(instance_path, 'app.db'))
    
    print('\n=== All migrations completed! ===')
