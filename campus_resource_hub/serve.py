#!/usr/bin/env python
"""Simple WSGI server using wsgiref (pure Python, cross-platform)."""
import os
import sys
from pathlib import Path
from wsgiref.simple_server import make_server
import logging

# Load environment variables from .env file BEFORE importing app
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set environment for production
os.environ['FLASK_ENV'] = 'production'

# Import app
from app import app

if __name__ == '__main__':
    print("=" * 60, flush=True)
    print("Campus Resource Hub - Flask Application", flush=True)
    print("=" * 60, flush=True)
    print("Starting WSGI server on http://127.0.0.1:5000", flush=True)
    print("Press CTRL+C to stop\n", flush=True)
    sys.stdout.flush()
    
    try:
        # Create WSGI server
        server = make_server('127.0.0.1', 5000, app)
        print(f"✓ Server listening on http://127.0.0.1:5000", flush=True)
        print(f"✓ Visit http://127.0.0.1:5000/concierge to test\n", flush=True)
        sys.stdout.flush()
        
        # Run server - handle exceptions gracefully
        while True:
            try:
                server.handle_request()  # Handle one request at a time
            except Exception as request_error:
                print(f"Request error: {request_error}", flush=True)
                import traceback
                traceback.print_exc()
                # Continue serving after error
                continue
        
    except KeyboardInterrupt:
        print("\n\n✗ Server stopped by user", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"✗ ERROR: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
