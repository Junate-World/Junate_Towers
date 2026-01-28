"""Vercel serverless entrypoint for the Flask app.

This file exports a WSGI `app` object that @vercel/python detects automatically.
"""
import os
from app import create_app

flask_config = os.getenv('FLASK_CONFIG', 'production')
app = create_app(flask_config)
