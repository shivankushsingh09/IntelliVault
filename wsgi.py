"""
WSGI entry point for IntelliVault
Use with Gunicorn or other WSGI application servers
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app

# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    # This is used by `gunicorn` or other WSGI servers
    app.run()
