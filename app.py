import os
from app import create_app, db
from app.models import TowerCategory, TowerVariant, TowerDocument

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'TowerCategory': TowerCategory, 'TowerVariant': TowerVariant, 'TowerDocument': TowerDocument}

if __name__ == '__main__':
    app.run(debug=True)
