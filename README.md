# Tower Documentation System

A modern, web-based documentation system for telecommunication tower technical drawings and specifications built with Flask.

## Features

- **Category-driven browsing**: Organize towers by type (Monopole, Lattice, Guyed, etc.)
- **PDF document management**: Upload and display multi-page technical drawings
- **Modern responsive UI**: Built with Tailwind CSS for professional engineering use
- **Cloud storage support**: Compatible with S3/Wasabi for scalable file storage
- **Version control**: Track document versions and maintain history
- **Search functionality**: Find towers by code, type, or category
- **Admin interface**: Complete content management system
- **Mobile-friendly**: Responsive design for all devices

## Technology Stack

- **Backend**: Python 3.8+, Flask 2.3+, SQLAlchemy
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Storage**: Local filesystem or S3-compatible cloud storage
- **File Processing**: PyPDF2 for PDF metadata extraction

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project files**
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**:
   ```bash
   flask run
   ```

7. **Access the application**:
   - Main site: http://localhost:5000
   - Admin panel: http://localhost:5000/admin
   - Default admin credentials: admin/admin123

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///tower_docs.db

# Cloud Storage (optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=tower-documents
AWS_S3_REGION=us-east-1
AWS_S3_ENDPOINT_URL=https://s3.us-east-1.wasabisys.com

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Production Setup

For production deployment:

### Deploying on Vercel with Supabase (Postgres) and Cloudinary (PDFs)

This project is configured to run serverlessly on Vercel, using:
- Supabase Postgres as the database
- Cloudinary to store PDF files (resource_type=raw)

#### 1) Prerequisites
- Supabase project (Database URL)
- Cloudinary account (CLOUDINARY_URL)
- Vercel account linked to your Git repository

#### 2) Environment Variables
Set these in Vercel → Project → Settings → Environment Variables (Production):

- SECRET_KEY: strong-random-string
- FLASK_CONFIG: production
- DATABASE_URL: Supabase SQLAlchemy URL (include sslmode=require)
  - Example: `postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB?sslmode=require`
- CLOUDINARY_URL: `cloudinary://<api_key>:<api_secret>@<cloud_name>`
- ADMIN_USERNAME: admin
- ADMIN_PASSWORD: your-strong-password

Optional (only if not using CLOUDINARY_URL):
- CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_FOLDER

#### 3) One-time DB setup against Supabase (run locally)
Vercel is read-only for file writes and not ideal for running migrations. Apply schema locally pointing to Supabase:

```
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create a .env file locally with DATABASE_URL pointing to Supabase
flask db init
flask db migrate -m "Initial tables"
flask db upgrade

# Optional: seed demo content into Supabase
python init_data.py
```

#### 4) Deploy to Vercel
- Ensure the repository contains:
  - `api/index.py` (Vercel entrypoint)
  - `vercel.json` (routes to Flask via vercel-wsgi)
- Push to your repo; import the project in Vercel and deploy.

#### 5) Static files
- Put public images in `app/static/images/...`
- Reference in templates using `{{ url_for('static', filename='images/hero.jpg') }}`
- The homepage slider accepts either relative paths (e.g., `images/hero.jpg`) or absolute URLs.

#### 6) PDFs in Cloudinary
- Admin uploads will store PDFs in Cloudinary (as `raw` resources) and save the secure URL in the database.
- Documents will render via that URL (iframe/embed).

#### 7) Troubleshooting
- 500 errors on production: confirm migrations ran on Supabase (`flask db upgrade`).
- PDFs not visible: verify Cloudinary credentials and that the upload returned a URL.
- Static images missing: ensure the path is correct and the file exists under `app/static`.

1. **Use PostgreSQL**:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost/tower_docs
   ```

2. **Configure cloud storage** for file uploads
3. **Set `FLASK_ENV=production`**
4. **Use a proper WSGI server** (Gunicorn, uWSGI)
5. **Set up reverse proxy** (Nginx)

## Usage Guide

### Adding Content

1. **Access Admin Panel**: Navigate to `/admin` and log in
2. **Create Categories**: Add tower types (e.g., "Monopole Tower")
3. **Add Variants**: Create specific tower models with specifications
4. **Upload Documents**: Attach PDF technical drawings to variants

### Browsing Content

1. **Home Page**: Browse all tower categories
2. **Category Page**: View all variants in a category
3. **Variant Page**: View specifications and PDF drawings
4. **Search**: Find towers by code or type

### PDF Management

- **File Format**: PDF only, max 50MB
- **Version Control**: Each upload creates a new version
- **Viewing**: Inline PDF viewer with zoom and navigation
- **Download**: Direct download option for offline viewing

## Project Structure

```
tower-docs/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # SQLAlchemy models
│   ├── storage.py               # Cloud storage integration
│   ├── main/                    # Public routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/                   # Admin routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── category_detail.html
│   │   ├── variant_detail.html
│   │   ├── search_results.html
│   │   ├── 404.html
│   │   ├── 500.html
│   │   └── admin/
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── categories.html
│   │       ├── category_form.html
│   │       ├── variants.html
│   │       ├── variant_form.html
│   │       ├── documents.html
│   │       └── document_form.html
│   └── static/                  # Static assets
│       ├── css/
│       │   └── custom.css
│       └── js/
│           └── main.js
├── uploads/                     # Local file storage
├── config.py                    # Configuration
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## API Endpoints

### Public Routes
- `GET /` - Home page (categories list)
- `GET /category/<id>` - Category detail page
- `GET /variant/<id>` - Variant detail page
- `GET /search?q=<query>` - Search results

### Admin Routes
- `GET /admin/` - Dashboard
- `GET /admin/login` - Admin login
- `GET|POST /admin/categories` - Manage categories
- `GET|POST /admin/category/new` - Create category
- `GET|POST /admin/category/<id>/edit` - Edit category
- `POST /admin/category/<id>/delete` - Delete category
- `GET|POST /admin/variants` - Manage variants
- `GET|POST /admin/variant/new` - Create variant
- `GET|POST /admin/variant/<id>/edit` - Edit variant
- `POST /admin/variant/<id>/delete` - Delete variant
- `GET|POST /admin/documents` - Manage documents
- `GET|POST /admin/variant/<id>/upload` - Upload document

## Database Schema

### TowerCategory
- `id` (Primary Key)
- `name` (Unique)
- `description`
- `thumbnail_url`
- `created_at`, `updated_at`

### TowerVariant
- `id` (Primary Key)
- `tower_code` (Unique)
- `height`
- `structural_type`
- `load_class`
- `engineering_notes`
- `category_id` (Foreign Key)

### TowerDocument
- `id` (Primary Key)
- `variant_id` (Foreign Key)
- `pdf_url`
- `page_count`
- `version`
- `file_size`
- `upload_timestamp`
- `is_active`

## Security Features

- **Admin Authentication**: HTTP Basic Auth for admin access
- **File Validation**: PDF-only uploads with size limits
- **CSRF Protection**: Flask-WTF forms with CSRF tokens
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Jinja2 auto-escaping

## Performance Optimizations

- **Database Indexing**: Tower codes, heights, and names
- **Lazy Loading**: PDF documents load on demand
- **CDN Support**: Cloud storage for static files
- **Responsive Images**: Optimized thumbnails
- **Caching**: Browser caching for static assets

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check `DATABASE_URL` in `.env`
   - Ensure database server is running

2. **File Upload Fails**:
   - Check file size (max 50MB)
   - Verify PDF format
   - Check storage permissions

3. **Admin Login Issues**:
   - Verify credentials in `.env`
   - Check `ADMIN_USERNAME` and `ADMIN_PASSWORD`

4. **PDF Not Displaying**:
   - Check browser PDF viewer support
   - Verify file URL accessibility
   - Check CORS settings for cloud storage

### Development Tips

- Use `flask shell` for database operations
- Enable debug mode for development
- Check browser console for JavaScript errors
- Monitor Flask logs for application errors

## Contributing

1. Follow PEP 8 Python style guidelines
2. Use semantic versioning for releases
3. Test file uploads with various PDF sizes
4. Validate responsive design on mobile devices
5. Document new features in README

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or questions:
- Check the troubleshooting section
- Review the configuration guide
- Test with the provided sample data
#   J u n a t e _ T o w e r s  
 