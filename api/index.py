"""Vercel serverless entrypoint for the Flask app using vercel-wsgi."""
import os
from vercel_wsgi import handle as vercel_handle
from app import create_app

flask_config = os.getenv('FLASK_CONFIG', 'production')
app = create_app(flask_config)

def handler(event, context):
    return vercel_handle(app, event, context)
