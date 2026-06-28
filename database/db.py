"""
Database utilities and initialization
"""
from database.models import db, User, Document, Note, Quiz, QuizAttempt, ChatSession, ChatMessage
from flask import current_app
import os


def init_db(app):
    """Initialize database"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['VECTOR_DB_FOLDER'], exist_ok=True)
        print("✓ Directories created successfully")


def drop_db(app):
    """Drop all database tables - USE WITH CAUTION"""
    with app.app_context():
        db.drop_all()
        print("✓ All database tables dropped")


def seed_db(app):
    """Seed database with sample data (for development)"""
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("Database already has data. Skipping seed.")
            return
        
        # Create demo user
        demo_user = User(
            username='demouser',
            email='demo@intellivault.com',
            full_name='Demo User',
            bio='This is a demo account for testing IntelliVault'
        )
        demo_user.set_password('demo123')
        demo_user.is_email_verified = True
        
        db.session.add(demo_user)
        db.session.commit()
        
        print("✓ Demo user created (username: demouser, password: demo123)")


def get_db_stats(app):
    """Get database statistics"""
    with app.app_context():
        stats = {
            'users': User.query.count(),
            'documents': Document.query.count(),
            'notes': Note.query.count(),
            'quizzes': Quiz.query.count(),
            'chat_sessions': ChatSession.query.count(),
        }
        return stats


def export_user_data(user_id):
    """Export all user data (for GDPR compliance)"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    data = {
        'user': user.to_dict(),
        'documents': [doc.to_dict() for doc in user.documents],
        'notes': [note.to_dict() for note in user.notes],
        'quizzes': [quiz.to_dict() for quiz in user.quizzes],
    }
    return data


def delete_user_data(user_id):
    """Delete all user data (for GDPR compliance)"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Delete related records
    ChatSession.query.filter_by(user_id=user_id).delete()
    Quiz.query.filter_by(user_id=user_id).delete()
    Note.query.filter_by(user_id=user_id).delete()
    Document.query.filter_by(user_id=user_id).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    return True
