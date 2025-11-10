#!/usr/bin/env python
"""Simple server runner."""
import os
import sys
import traceback

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Campus Resource Hub - Starting Server")
print("=" * 60)

try:
    print("Importing app...")
    from app import app
    print("✓ App imported successfully")
    
    print("Server URL: http://127.0.0.1:5000")
    print("Press CTRL+C to stop")
    print("=" * 60)
    
    # Use Flask's built-in server
    print("Starting Flask server...")
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
except KeyboardInterrupt:
    print("\n\nServer stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "=" * 60)
    input("Press Enter to exit...")
    sys.exit(1)
