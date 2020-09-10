from app import app, db
from app.models import Users, History, Watch

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Users': Users, 'Transactions': History, 'Watching': Watch}