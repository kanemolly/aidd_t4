"""Check registered Flask routes."""
import sys
sys.dont_write_bytecode = True

# Monkey patch to prevent server from starting
import werkzeug.serving
werkzeug.serving.run_simple = lambda *args, **kwargs: None

from app import app

print("\n=== Registered Routes ===")
with app.app_context():
    bookings_routes = []
    all_routes = []
    for rule in app.url_map.iter_rules():
        all_routes.append((rule.rule, rule.endpoint, list(rule.methods)))
        if 'bookings' in rule.endpoint:
            bookings_routes.append((rule.rule, rule.endpoint, list(rule.methods)))
    
    print("\nBookings-related routes:")
    for route in sorted(bookings_routes):
        print(f"  {route[0]:40} -> {route[1]:30} {route[2]}")
    
    print(f"\nTotal routes registered: {len(all_routes)}")
    
    # Check specifically for dashboard
    dashboard_routes = [r for r in all_routes if 'dashboard' in r[0]]
    print("\nDashboard routes:")
    for route in dashboard_routes:
        print(f"  {route[0]:40} -> {route[1]:30} {route[2]}")
