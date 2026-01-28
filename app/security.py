"""
Security utilities for Tower Documentation System
"""

from functools import wraps
from flask import request, redirect, url_for, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import re

class SecurityManager:
    """Handle security-related operations"""
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate a cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is valid"
    
    @staticmethod
    def hash_password(password):
        """Hash a password securely"""
        return generate_password_hash(password)
    
    @staticmethod
    def verify_password(hashed_password, password):
        """Verify a password against its hash"""
        return check_password_hash(hashed_password, password)
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent directory traversal"""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)  # Remove directory traversal
        filename = filename.strip('. ')  # Remove leading/trailing dots and spaces
        
        # Limit filename length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename
    
    @staticmethod
    def validate_file_upload(file):
        """Validate uploaded file for security"""
        # Check file extension
        allowed_extensions = {'pdf'}
        if '.' not in file.filename:
            return False, "File must have an extension"
        
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension not in allowed_extensions:
            return False, f"Only {', '.join(allowed_extensions)} files are allowed"
        
        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024
        if hasattr(file, 'content_length') and file.content_length > max_size:
            return False, "File size must be less than 50MB"
        
        # Check MIME type
        if file.mimetype != 'application/pdf':
            return False, "File must be a PDF"
        
        return True, "File is valid"

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session-based auth first
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        
        # Fall back to HTTP Basic Auth
        auth = request.authorization
        if not auth:
            return redirect(url_for('admin.login'))
        
        if (auth.username == current_app.config['ADMIN_USERNAME'] and 
            auth.password == current_app.config['ADMIN_PASSWORD']):
            # Set session for future requests
            session['admin_logged_in'] = True
            session.permanent = True
            return f(*args, **kwargs)
        
        return redirect(url_for('admin.login'))
    
    return decorated_function

def csrf_protect():
    """Generate CSRF token for forms"""
    if 'csrf_token' not in session:
        session['csrf_token'] = SecurityManager.generate_secure_token()
    return session['csrf_token']

def verify_csrf_token(token):
    """Verify CSRF token"""
    return token == session.get('csrf_token')

def rate_limit_check(identifier, limit=5, window=300):
    """Simple rate limiting implementation"""
    # This is a basic implementation - in production, use Redis or similar
    if 'rate_limits' not in session:
        session['rate_limits'] = {}
    
    now = int(datetime.utcnow().timestamp())
    key = f"{identifier}:{now // window}"
    
    if key not in session['rate_limits']:
        session['rate_limits'][key] = 0
    
    session['rate_limits'][key] += 1
    
    # Clean old entries
    old_keys = [k for k in session['rate_limits'].keys() 
                if int(k.split(':')[-1]) < (now // window) - 1]
    for old_key in old_keys:
        del session['rate_limits'][old_key]
    
    return session['rate_limits'][key] <= limit

def validate_input(data, rules):
    """Validate input data against rules"""
    errors = {}
    
    for field, rule in rules.items():
        value = data.get(field, '')
        
        # Required validation
        if rule.get('required', False) and not value.strip():
            errors[field] = f"{field.replace('_', ' ').title()} is required"
            continue
        
        if not value:
            continue
        
        # Type validation
        if 'type' in rule:
            if rule['type'] == 'email':
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    errors[field] = "Invalid email format"
            
            elif rule['type'] == 'url':
                url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
                if not re.match(url_pattern, value):
                    errors[field] = "Invalid URL format"
            
            elif rule['type'] == 'numeric':
                try:
                    float(value)
                except ValueError:
                    errors[field] = "Must be a number"
        
        # Length validation
        if 'min_length' in rule and len(value) < rule['min_length']:
            errors[field] = f"Must be at least {rule['min_length']} characters"
        
        if 'max_length' in rule and len(value) > rule['max_length']:
            errors[field] = f"Must be no more than {rule['max_length']} characters"
        
        # Pattern validation
        if 'pattern' in rule:
            if not re.match(rule['pattern'], value):
                errors[field] = rule.get('error_message', 'Invalid format')
    
    return errors

# Security headers middleware
def add_security_headers(response):
    """Add security headers to responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "connect-src 'self'; "
        "frame-src 'self';"
    )
    return response
