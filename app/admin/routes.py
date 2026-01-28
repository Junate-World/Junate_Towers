from flask import render_template, request, redirect, url_for, flash, current_app, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, FileField, PasswordField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, URL, Optional
from werkzeug.utils import secure_filename
from app.admin import bp
from app.models import TowerCategory, TowerVariant, TowerDocument, Slider, allowed_file
from app import db
from app.storage import storage
import os

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    thumbnail_url = StringField('Thumbnail URL')
    submit = SubmitField('Save Category')

class VariantForm(FlaskForm):
    tower_code = StringField('Tower Code', validators=[DataRequired(), Length(min=2, max=50)])
    height = FloatField('Height (meters)', validators=[DataRequired(), NumberRange(min=0)])
    structural_type = SelectField('Structural Type', 
                                choices=[('self-supporting', 'Self-Supporting'),
                                        ('guyed', 'Guyed'),
                                        ('monopole', 'Monopole')],
                                validators=[DataRequired()])
    load_class = StringField('Load Class')
    engineering_notes = TextAreaField('Engineering Notes')
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Variant')

class DocumentForm(FlaskForm):
    pdf_file = FileField('PDF File', validators=[DataRequired()])
    version = StringField('Version', default='1.0')
    submit = SubmitField('Upload Document')

class SliderForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description')
    image_url = StringField('Image URL', validators=[DataRequired(), URL()])
    link_url = StringField('Link URL', validators=[Optional(), URL()])
    order = IntegerField('Display Order', default=0, validators=[NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Slider')

# Admin authentication decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('You must be logged in to access this page.', 'error')
            # Preserve intended destination
            return redirect(url_for('admin.login', next=request.full_path))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Form-based admin login"""
    form = LoginForm()
    next_url = request.args.get('next') or request.form.get('next')
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            session.permanent = True
            flash('Login successful!', 'success')
            # Redirect to original destination if provided and safe
            if next_url and not next_url.startswith(('http://', 'https://')):
                return redirect(next_url)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('admin/login.html', form=form, next_url=next_url)

@bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

@bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard"""
    categories_count = TowerCategory.query.count()
    variants_count = TowerVariant.query.count()
    documents_count = TowerDocument.query.count()
    
    recent_categories = TowerCategory.query.order_by(TowerCategory.created_at.desc()).limit(5).all()
    recent_variants = TowerVariant.query.order_by(TowerVariant.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         categories_count=categories_count,
                         variants_count=variants_count,
                         documents_count=documents_count,
                         recent_categories=recent_categories,
                         recent_variants=recent_variants)

# Category management
@bp.route('/categories')
@admin_required
def categories():
    """List all categories"""
    categories = TowerCategory.query.order_by(TowerCategory.name).all()
    return render_template('admin/categories.html', categories=categories)

@bp.route('/category/new', methods=['GET', 'POST'])
@admin_required
def new_category():
    """Create new category"""
    form = CategoryForm()
    if form.validate_on_submit():
        category = TowerCategory(
            name=form.name.data,
            description=form.description.data,
            thumbnail_url=form.thumbnail_url.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html', form=form, title='New Category')

@bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """Edit existing category"""
    category = TowerCategory.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.thumbnail_url = form.thumbnail_url.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html', form=form, category=category, title='Edit Category')

@bp.route('/category/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    """Delete category"""
    category = TowerCategory.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.categories'))

# Variant management
@bp.route('/variants')
@admin_required
def variants():
    """List all variants"""
    variants = TowerVariant.query.order_by(TowerVariant.tower_code).all()
    return render_template('admin/variants.html', variants=variants)

@bp.route('/variant/new', methods=['GET', 'POST'])
@admin_required
def new_variant():
    """Create new variant"""
    form = VariantForm()
    form.category_id.choices = [(c.id, c.name) for c in TowerCategory.query.order_by('name').all()]
    
    if form.validate_on_submit():
        variant = TowerVariant(
            tower_code=form.tower_code.data,
            height=form.height.data,
            structural_type=form.structural_type.data,
            load_class=form.load_class.data,
            engineering_notes=form.engineering_notes.data,
            category_id=form.category_id.data
        )
        db.session.add(variant)
        db.session.commit()
        flash('Variant created successfully!', 'success')
        # Redirect straight to upload PDF for this new variant
        return redirect(url_for('admin.upload_document', variant_id=variant.id))
    
    return render_template('admin/variant_form.html', form=form, title='New Variant')

@bp.route('/variant/<int:variant_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_variant(variant_id):
    """Edit existing variant"""
    variant = TowerVariant.query.get_or_404(variant_id)
    form = VariantForm(obj=variant)
    form.category_id.choices = [(c.id, c.name) for c in TowerCategory.query.order_by('name').all()]
    
    if form.validate_on_submit():
        variant.tower_code = form.tower_code.data
        variant.height = form.height.data
        variant.structural_type = form.structural_type.data
        variant.load_class = form.load_class.data
        variant.engineering_notes = form.engineering_notes.data
        variant.category_id = form.category_id.data
        db.session.commit()
        flash('Variant updated successfully!', 'success')
        return redirect(url_for('admin.variants'))
    
    return render_template('admin/variant_form.html', form=form, variant=variant, title='Edit Variant')

@bp.route('/variant/<int:variant_id>/delete', methods=['POST'])
@admin_required
def delete_variant(variant_id):
    """Delete variant"""
    variant = TowerVariant.query.get_or_404(variant_id)
    db.session.delete(variant)
    db.session.commit()
    flash('Variant deleted successfully!', 'success')
    return redirect(url_for('admin.variants'))

# Document management
@bp.route('/documents')
@admin_required
def documents():
    """List all documents"""
    documents = TowerDocument.query.order_by(TowerDocument.upload_timestamp.desc()).all()
    return render_template('admin/documents.html', documents=documents)

@bp.route('/variant/<int:variant_id>/upload', methods=['GET', 'POST'])
@admin_required
def upload_document(variant_id):
    """Upload PDF document for variant"""
    variant = TowerVariant.query.get_or_404(variant_id)
    form = DocumentForm()
    
    if form.validate_on_submit():
        file = form.pdf_file.data
        if file and allowed_file(file.filename):
            # Deactivate existing documents
            TowerDocument.query.filter_by(variant_id=variant_id).update({'is_active': False})
            
            # Get PDF info
            pdf_info = storage.get_pdf_info(file)
            
            # Upload file
            filename = secure_filename(f"{variant.tower_code}_{form.version.data}.pdf")
            pdf_url = storage.upload_file(file, filename)
            
            if pdf_url:
                document = TowerDocument(
                    variant_id=variant_id,
                    pdf_url=pdf_url,
                    page_count=pdf_info['page_count'],
                    file_size=pdf_info['file_size'],
                    version=form.version.data,
                    is_active=True
                )
                db.session.add(document)
                db.session.commit()
                flash('Document uploaded successfully!', 'success')
                return redirect(url_for('admin.documents'))
            else:
                flash('Error uploading file!', 'error')
        else:
            flash('Invalid file type. Please upload a PDF file.', 'error')
    
    return render_template('admin/document_form.html', form=form, variant=variant)

# Slider management
@bp.route('/sliders')
@admin_required
def sliders():
    """Manage homepage sliders"""
    sliders = Slider.query.order_by(Slider.order, Slider.created_at.desc()).all()
    return render_template('admin/sliders.html', sliders=sliders)

@bp.route('/slider/new', methods=['GET', 'POST'])
@admin_required
def new_slider():
    """Create new slider"""
    form = SliderForm()
    
    if form.validate_on_submit():
        slider = Slider(
            title=form.title.data,
            description=form.description.data,
            image_url=form.image_url.data,
            link_url=form.link_url.data,
            order=form.order.data,
            is_active=form.is_active.data
        )
        db.session.add(slider)
        db.session.commit()
        flash('Slider created successfully!', 'success')
        return redirect(url_for('admin.sliders'))
    
    return render_template('admin/slider_form.html', form=form, title='New Slider')

@bp.route('/slider/<int:slider_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_slider(slider_id):
    """Edit existing slider"""
    slider = Slider.query.get_or_404(slider_id)
    form = SliderForm(obj=slider)
    
    if form.validate_on_submit():
        slider.title = form.title.data
        slider.description = form.description.data
        slider.image_url = form.image_url.data
        slider.link_url = form.link_url.data
        slider.order = form.order.data
        slider.is_active = form.is_active.data
        db.session.commit()
        flash('Slider updated successfully!', 'success')
        return redirect(url_for('admin.sliders'))
    
    return render_template('admin/slider_form.html', form=form, slider=slider, title='Edit Slider')

@bp.route('/slider/<int:slider_id>/delete', methods=['POST'])
@admin_required
def delete_slider(slider_id):
    """Delete slider"""
    slider = Slider.query.get_or_404(slider_id)
    db.session.delete(slider)
    db.session.commit()
    flash('Slider deleted successfully!', 'success')
    return redirect(url_for('admin.sliders'))
