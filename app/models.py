from datetime import datetime
from app import db

class Slider(db.Model):
    __tablename__ = 'sliders'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    link_url = db.Column(db.String(500))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Slider {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'link_url': self.link_url,
            'order': self.order,
            'is_active': self.is_active
        }

class TowerCategory(db.Model):
    __tablename__ = 'tower_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with variants
    variants = db.relationship('TowerVariant', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TowerCategory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'variant_count': self.variants.count()
        }

class TowerVariant(db.Model):
    __tablename__ = 'tower_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    tower_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    height = db.Column(db.Float, nullable=False, index=True)
    structural_type = db.Column(db.String(50), nullable=False, index=True)
    load_class = db.Column(db.String(20))
    engineering_notes = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('tower_categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with documents
    documents = db.relationship('TowerDocument', backref='variant', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TowerVariant {self.tower_code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tower_code': self.tower_code,
            'height': self.height,
            'structural_type': self.structural_type,
            'load_class': self.load_class,
            'engineering_notes': self.engineering_notes,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'document_count': self.documents.count()
        }

class TowerDocument(db.Model):
    __tablename__ = 'tower_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('tower_variants.id'), nullable=False)
    pdf_url = db.Column(db.String(500), nullable=False)
    page_count = db.Column(db.Integer)
    version = db.Column(db.String(20), default='1.0')
    file_size = db.Column(db.Integer)  # in bytes
    upload_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<TowerDocument {self.id} for {self.variant.tower_code if self.variant else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'variant_id': self.variant_id,
            'tower_code': self.variant.tower_code if self.variant else None,
            'pdf_url': self.pdf_url,
            'page_count': self.page_count,
            'version': self.version,
            'file_size': self.file_size,
            'upload_timestamp': self.upload_timestamp.isoformat() if self.upload_timestamp else None,
            'is_active': self.is_active
        }

# Helper function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
