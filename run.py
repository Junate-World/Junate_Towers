#!/usr/bin/env python3
"""
Development server for Tower Documentation System
"""

import os
from app import create_app, db
from app.models import TowerCategory, TowerVariant, TowerDocument

# Create Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db, 
        'TowerCategory': TowerCategory, 
        'TowerVariant': TowerVariant, 
        'TowerDocument': TowerDocument
    }

@app.before_request
def create_tables():
    """Create database tables if they don't exist"""
    if not hasattr(app, '_tables_created'):
        db.create_all()
        app._tables_created = True

if __name__ == '__main__':
    # Development server configuration
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
