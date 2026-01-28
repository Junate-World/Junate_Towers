#!/usr/bin/env python3
"""
Initialize the Tower Documentation System with sample data
"""

import os
from datetime import datetime
from app import create_app, db
from app.models import TowerCategory, TowerVariant, TowerDocument, Slider

def create_sample_data():
    """Create sample tower categories, variants, and documents"""
    
    app = create_app('development')
    
    with app.app_context():
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        
        # Clear existing data
        print("Clearing existing data...")
        TowerDocument.query.delete()
        TowerVariant.query.delete()
        TowerCategory.query.delete()
        Slider.query.delete()
        db.session.commit()
        
        # Create categories
        print("Creating tower categories...")
        categories = [
            TowerCategory(
                name="Monopole Tower",
                description="Single-pole telecommunications towers suitable for urban and suburban deployments. These structures offer minimal footprint and aesthetic appeal."
            ),
            TowerCategory(
                name="3-Leg Lattice Tower",
                description="Triangular lattice towers providing excellent stability and wind resistance. Ideal for medium-height installations requiring robust construction."
            ),
            TowerCategory(
                name="4-Leg Lattice Tower",
                description="Square lattice towers offering maximum stability for heavy equipment loads. Commonly used for broadcast and telecommunications applications."
            ),
            TowerCategory(
                name="Guyed Mast",
                description="Economical tall towers supported by guy wires. Perfect for radio transmission and telecommunications requiring significant height."
            )
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.commit()
        
        # Create variants
        print("Creating tower variants...")
        variants = [
            # Monopole variants
            TowerVariant(
                tower_code="MP-30-001",
                height=30.0,
                structural_type="monopole",
                load_class="Class A",
                engineering_notes="Standard urban monopole with 3-platform configuration. Suitable for cellular equipment installation.",
                category_id=categories[0].id
            ),
            TowerVariant(
                tower_code="MP-45-002",
                height=45.0,
                structural_type="monopole",
                load_class="Class B",
                engineering_notes="Heavy-duty monopole with reinforced base. Designed for multiple carrier equipment.",
                category_id=categories[0].id
            ),
            TowerVariant(
                tower_code="MP-60-003",
                height=60.0,
                structural_type="monopole",
                load_class="Class B",
                engineering_notes="Tall monopole with specialized foundation requirements. Includes lightning protection system.",
                category_id=categories[0].id
            ),
            
            # 3-Leg Lattice variants
            TowerVariant(
                tower_code="LT3-40-001",
                height=40.0,
                structural_type="self-supporting",
                load_class="Medium",
                engineering_notes="Standard 3-leg lattice tower with bolted connections. Easy assembly and maintenance access.",
                category_id=categories[1].id
            ),
            TowerVariant(
                tower_code="LT3-55-002",
                height=55.0,
                structural_type="self-supporting",
                load_class="Heavy",
                engineering_notes="Reinforced 3-leg design for high-wind areas. Includes climbing ladder and safety systems.",
                category_id=categories[1].id
            ),
            TowerVariant(
                tower_code="LT3-70-003",
                height=70.0,
                structural_type="self-supporting",
                load_class="Heavy",
                engineering_notes="Tall 3-leg lattice with intermediate platforms. Designed for broadcast equipment.",
                category_id=categories[1].id
            ),
            
            # 4-Leg Lattice variants
            TowerVariant(
                tower_code="LT4-50-001",
                height=50.0,
                structural_type="self-supporting",
                load_class="Heavy",
                engineering_notes="Standard 4-leg lattice tower with square cross-section. Maximum stability for heavy antennas.",
                category_id=categories[2].id
            ),
            TowerVariant(
                tower_code="LT4-75-002",
                height=75.0,
                structural_type="self-supporting",
                load_class="Extra Heavy",
                engineering_notes="Heavy-duty 4-leg tower with enlarged base. Suitable for large dish antennas and broadcast arrays.",
                category_id=categories[2].id
            ),
            TowerVariant(
                tower_code="LT4-100-003",
                height=100.0,
                structural_type="self-supporting",
                load_class="Extra Heavy",
                engineering_notes="Mega-tower 4-leg design with multiple working platforms. Requires specialized installation equipment.",
                category_id=categories[2].id
            ),
            
            # Guyed Mast variants
            TowerVariant(
                tower_code="GM-60-001",
                height=60.0,
                structural_type="guyed",
                load_class="Medium",
                engineering_notes="Standard guyed mast with 3-level guy wire configuration. Economical solution for radio transmission.",
                category_id=categories[3].id
            ),
            TowerVariant(
                tower_code="GM-90-002",
                height=90.0,
                structural_type="guyed",
                load_class="Medium",
                engineering_notes="Tall guyed mast with 4-level guy wire system. Includes aircraft warning lighting.",
                category_id=categories[3].id
            ),
            TowerVariant(
                tower_code="GM-120-003",
                height=120.0,
                structural_type="guyed",
                load_class="Light",
                engineering_notes="Ultra-tall guyed mast for specialized applications. Requires extensive guy wire anchor field.",
                category_id=categories[3].id
            )
        ]
        
        for variant in variants:
            db.session.add(variant)
        db.session.commit()
        
        # Create sample documents (placeholder URLs)
        print("Creating sample documents...")
        documents = []
        for i, variant in enumerate(variants):
            # Create one document per variant
            doc = TowerDocument(
                variant_id=variant.id,
                pdf_url=f"/uploads/sample_{variant.tower_code}.pdf",
                page_count=5 + (i % 3),  # 5-7 pages
                version="1.0",
                file_size=2048000 + (i * 500000),  # 2-7MB
                is_active=True
            )
            documents.append(doc)
        
        for doc in documents:
            db.session.add(doc)
        db.session.commit()
        
        # Create sample sliders
        print("Creating sample sliders...")
        sliders = [
            Slider(
                title="Professional Tower Solutions",
                description="Engineered for excellence in telecommunications infrastructure",
                image_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1920&h=600&fit=crop",
                link_url="{{ url_for('main.index') }}",
                order=1,
                is_active=True
            ),
            Slider(
                title="Advanced Lattice Technology",
                description="Robust designs for challenging environments",
                image_url="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1920&h=600&fit=crop",
                link_url="{{ url_for('main.index') }}",
                order=2,
                is_active=True
            ),
            Slider(
                title="Innovative Engineering",
                description="Cutting-edge solutions for modern connectivity",
                image_url="https://images.unsplash.com/photo-1517245386807-bb74f2890370?w=1920&h=600&fit=crop",
                link_url="{{ url_for('main.index') }}",
                order=3,
                is_active=True
            )
        ]
        
        for slider in sliders:
            db.session.add(slider)
        db.session.commit()
        
        print(f"Sample data created successfully!")
        print(f"Created {len(categories)} categories")
        print(f"Created {len(variants)} tower variants")
        print(f"Created {len(documents)} sample documents")
        print(f"Created {len(sliders)} homepage sliders")
        print(f"\nYou can now start the application with: python run.py")
        print(f"Visit http://localhost:5000 to view the system")
        print(f"Admin login: admin/admin123 at http://localhost:5000/admin")

if __name__ == '__main__':
    create_sample_data()
