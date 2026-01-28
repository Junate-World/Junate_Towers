from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from app.main import bp
from app.models import TowerCategory, TowerVariant, TowerDocument, Slider
from app import db

@bp.route('/')
def index():
    """Home page - Display all tower categories"""
    categories = TowerCategory.query.order_by(TowerCategory.name).all()
    total_variants = TowerVariant.query.count()
    total_documents = TowerDocument.query.count()
    sliders = Slider.query.filter_by(is_active=True).order_by(Slider.order).all()
    return render_template('index.html', categories=categories, total_variants=total_variants, total_documents=total_documents, sliders=sliders)

@bp.route('/category/<int:category_id>')
def category_detail(category_id):
    """Tower category page - Display all variants in a category"""
    category = TowerCategory.query.get_or_404(category_id)
    variants = TowerVariant.query.filter_by(category_id=category_id)\
                                .order_by(TowerVariant.height)\
                                .all()
    return render_template('category_detail.html', category=category, variants=variants)

@bp.route('/health')
def health():
    """Lightweight health check for uptime monitors."""
    status = {
        'app': 'ok',
        'db': 'unknown',
        'cloudinary_configured': False,
    }
    # DB check
    try:
        db.session.execute(db.text('SELECT 1'))
        status['db'] = 'ok'
    except Exception as e:
        status['db'] = f'error: {type(e).__name__}'
    # Cloudinary config presence (no outbound call)
    try:
        from app.storage import cloudinary as _cloud
        cfg = getattr(_cloud, 'config', None)
        status['cloudinary_configured'] = bool(cfg and cfg().cloud_name)
    except Exception:
        status['cloudinary_configured'] = False
    return jsonify(status), 200 if status['db'] == 'ok' else 503
@bp.route('/variant/<int:variant_id>')
def variant_detail(variant_id):
    """Tower variant detail page - Display variant info and PDF"""
    variant = TowerVariant.query.get_or_404(variant_id)
    document = TowerDocument.query.filter_by(variant_id=variant_id, is_active=True)\
                                 .order_by(TowerDocument.upload_timestamp.desc())\
                                 .first()
    return render_template('variant_detail.html', variant=variant, document=document)

@bp.route('/search')
def search():
    """Search functionality for towers"""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.index'))
    
    # Search in tower codes, categories, and structural types
    variants = TowerVariant.query.filter(
        (TowerVariant.tower_code.ilike(f'%{query}%')) |
        (TowerVariant.structural_type.ilike(f'%{query}%'))
    ).all()
    
    categories = TowerCategory.query.filter(
        TowerCategory.name.ilike(f'%{query}%')
    ).all()
    
    return render_template('search_results.html', 
                         query=query, 
                         variants=variants, 
                         categories=categories)

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
