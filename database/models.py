"""
Database Models for IntelliVault
Defines all database schema and relationships
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    avatar_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    
    # Preferences
    theme = db.Column(db.String(50), default='light')
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    notes = db.relationship('Note', backref='author', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='owner', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='creator', lazy=True, cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'theme': self.theme,
            'notifications_enabled': self.notifications_enabled,
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Document(db.Model):
    """Document/PDF model"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    
    # File metadata
    file_size = db.Column(db.Integer)  # in bytes
    file_type = db.Column(db.String(50))  # pdf, txt, docx
    mime_type = db.Column(db.String(100))
    
    # Processing status
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    
    # Extracted content
    text_content = db.Column(db.Text)
    page_count = db.Column(db.Integer)
    
    # Vector storage info
    vector_store_path = db.Column(db.String(500))
    is_indexed = db.Column(db.Boolean, default=False)
    
    # Metadata
    tags = db.Column(db.String(500))  # comma-separated tags
    is_favorite = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('Note', backref='document', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'status': self.status,
            'page_count': self.page_count,
            'is_indexed': self.is_indexed,
            'is_favorite': self.is_favorite,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<Document {self.title}>'


class Note(db.Model):
    """Notes model for user notes on documents"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Note type
    note_type = db.Column(db.String(50), default='manual')  # manual, summary, annotation
    
    # Highlight info (for annotations)
    page_number = db.Column(db.Integer)
    highlight_text = db.Column(db.Text)
    
    # Metadata
    color = db.Column(db.String(50), default='yellow')  # for highlighting
    is_pinned = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(500))  # comma-separated
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'note_type': self.note_type,
            'page_number': self.page_number,
            'color': self.color,
            'is_pinned': self.is_pinned,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<Note {self.title}>'


class Quiz(db.Model):
    """Quiz model for generated quizzes from documents"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Quiz data stored as JSON
    questions_data = db.Column(db.Text, nullable=False)  # JSON array of questions
    
    # Metadata
    question_count = db.Column(db.Integer)
    difficulty = db.Column(db.String(50))  # easy, medium, hard
    
    # Performance tracking
    attempts_count = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Float, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def get_questions(self):
        """Get questions as list"""
        try:
            return json.loads(self.questions_data)
        except:
            return []
    
    def set_questions(self, questions):
        """Set questions from list"""
        self.questions_data = json.dumps(questions)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'question_count': self.question_count,
            'difficulty': self.difficulty,
            'attempts_count': self.attempts_count,
            'best_score': self.best_score,
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<Quiz {self.title}>'


class QuizAttempt(db.Model):
    """Track quiz attempts and scores"""
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
    
    # Responses stored as JSON
    responses_data = db.Column(db.Text)  # JSON object with question_id: answer
    
    # Scoring
    score = db.Column(db.Float)  # percentage 0-100
    correct_answers = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    
    # Timing
    time_spent_seconds = db.Column(db.Integer)
    
    # Timestamp
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'time_spent_seconds': self.time_spent_seconds,
            'attempted_at': self.attempted_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<QuizAttempt {self.quiz_id}>'


class ChatSession(db.Model):
    """Chat session for AI Q&A"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), default='Chat Session')
    
    # Session metadata
    is_active = db.Column(db.Boolean, default=True)
    model_used = db.Column(db.String(50), default='gpt-3.5-turbo')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'is_active': self.is_active,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat(),
            'message_count': len(self.messages),
        }
    
    def __repr__(self):
        return f'<ChatSession {self.id}>'


class ChatMessage(db.Model):
    """Individual chat messages"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False, index=True)
    
    role = db.Column(db.String(50), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    
    # Metadata
    tokens_used = db.Column(db.Integer)
    is_edited = db.Column(db.Boolean, default=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'
