#!/usr/bin/env python
"""
Development server runner for IntelliVault
Run this file to start the application in development mode
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from database.db import init_db

if __name__ == '__main__':
    # Create app
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    # Initialize database
    with app.app_context():
        init_db(app)
    
    # Run development server
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', True)
    )
