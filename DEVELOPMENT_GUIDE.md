# IntelliVault Development Guide

A comprehensive step-by-step guide to developing and extending the IntelliVault project.

## Table of Contents

1. [Setup](#setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Adding Features](#adding-features)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- PostgreSQL (optional, for production)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Intellivault
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

**Edit `.env`:**
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///intellivault.db
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-huggingface-key
```

### Step 5: Initialize Database

```bash
python run.py
```

The app will create the database and seed demo data on first run.

**Demo Credentials:**
- Username: `demouser`
- Password: `demo123`

---

## Project Structure

```
Intellivault/
├── app.py                          # Flask app factory
├── config.py                       # Configuration settings
├── run.py                          # Development server
├── wsgi.py                         # Production WSGI entry point
│
├── database/
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy models (User, Document, Note, etc.)
│   └── db.py                       # Database utilities
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                     # Authentication (register, login)
│   ├── dashboard.py                # Main dashboard and search
│   ├── notes.py                    # Notes CRUD operations
│   ├── pdf.py                      # PDF upload and processing
│   ├── ai.py                       # AI features (summarization, chat)
│   ├── quiz.py                     # Quiz management
│   └── profile.py                  # User profile and settings
│
├── ai/
│   ├── __init__.py
│   ├── summarizer.py               # Document summarization
│   ├── keyword.py                  # Keyword extraction
│   ├── embeddings.py               # Vector embeddings generation
│   ├── chatbot.py                  # AI chatbot
│   └── quiz_generator.py           # Automatic quiz creation
│
├── utils/
│   ├── __init__.py
│   ├── pdf_processor.py            # PDF text extraction
│   ├── validators.py               # Input validation
│   └── helpers.py                  # Helper functions
│
├── templates/
│   ├── base.html                   # Base template with navigation
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard.html              # Dashboard with stats
│   ├── notes.html                  # Notes list
│   ├── upload.html                 # PDF upload form
│   ├── chat.html                   # AI chat interface
│   ├── quiz/
│   │   ├── list.html
│   │   └── take.html
│   ├── profile.html                # User profile
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/
│   ├── css/
│   │   └── style.css               # Main stylesheet
│   ├── js/
│   │   ├── main.js                 # Core JavaScript
│   │   ├── api.js                  # API utilities
│   │   └── notes.js                # Notes functionality
│   └── img/
│       └── logo.png
│
├── logs/
│   └── intellivault.log            # Application logs
│
├── uploads/                         # User uploaded files
├── vector_db/                       # Vector database storage
│
├── .env                            # Environment variables (local)
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker container definition
├── docker-compose.yml              # Docker compose for local dev
├── Procfile                        # Heroku deployment
├── README.md                       # Project documentation
├── test_app.py                     # Tests
├── conftest.py                     # Pytest configuration
└── pytest.ini                      # Pytest settings
```

---

## Development Workflow

### 1. Start Development Server

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run development server
python run.py
```

Access the app at: `http://localhost:5000`

### 2. Create a New Feature

#### Example: Adding a New Route

**File: `routes/example.py`**

```python
from flask import Blueprint, render_template
from flask_login import login_required

example_bp = Blueprint('example', __name__, url_prefix='/example')

@example_bp.route('/')
@login_required
def list_items():
    """List all items"""
    return render_template('example/list.html')

@example_bp.route('/api/items', methods=['GET'])
@login_required
def get_items_api():
    """API endpoint to get items"""
    return {'items': []}, 200
```

**Register in `app.py`:**

```python
def register_blueprints(app):
    # ... existing blueprints ...
    from routes.example import example_bp
    app.register_blueprint(example_bp)
```

#### Example: Adding a New Model

**File: `database/models.py`**

```python
class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('items', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }
```

Then create and apply migrations:

```bash
# Create database tables
python
>>> from app import create_app
>>> from database.db import init_db
>>> app = create_app()
>>> with app.app_context():
...     init_db()
```

### 3. Best Practices

- **Keep routes modular**: One blueprint per feature
- **Use API endpoints**: Both HTML routes and JSON APIs
- **Validate input**: Use validators in `utils/validators.py`
- **Log important events**: Use Flask's logger
- **Write docstrings**: Document all functions and classes
- **Use SQLAlchemy models**: Don't write raw SQL

---

## Adding Features

### Feature: PDF Upload and Processing

**Step 1: Implement PDF Processor**

```python
# utils/pdf_processor.py
import PyPDF2
import pdfplumber

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def get_page_count(filepath):
    """Get PDF page count"""
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)
```

**Step 2: Update Routes**

```python
# routes/pdf.py
from flask import request, jsonify
from utils.pdf_processor import extract_text_from_pdf, get_page_count
from database.models import Document

@pdf_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_pdf_api():
    """Upload PDF file via API"""
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400
    
    file = request.files['file']
    doc = Document(filename=file.filename, user_id=current_user.id)
    # ... save file and process ...
    
    return {'document_id': doc.id}, 201
```

### Feature: AI Summarization

**Step 1: Implement Summarizer**

```python
# ai/summarizer.py
import openai

def summarize_text(text, max_length=500):
    """Summarize text using OpenAI"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Summarize: {text[:3000]}"}
        ]
    )
    return response['choices'][0]['message']['content']
```

**Step 2: Add to Routes**

```python
# routes/ai.py
@ai_bp.route('/api/summarize', methods=['POST'])
@login_required
def summarize_document():
    """Summarize a document"""
    data = request.get_json()
    doc = Document.query.get(data['document_id'])
    
    if not doc or doc.user_id != current_user.id:
        return {'error': 'Document not found'}, 404
    
    summary = summarize_text(doc.text_content)
    
    note = Note(
        title=f"Summary: {doc.title}",
        content=summary,
        note_type='summary',
        document_id=doc.id,
        user_id=current_user.id
    )
    db.session.add(note)
    db.session.commit()
    
    return note.to_dict(), 201
```

---

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test_app.py

# Run specific test
pytest test_app.py::TestAuth::test_register_user

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=.

# Skip slow tests
pytest -m "not slow"
```

### Write Tests

```python
# test_app.py or test_<feature>.py
def test_feature_name(client):
    """Test description"""
    response = client.get('/path')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'key' in data
```

### Testing Best Practices

- Test each endpoint (GET, POST, PUT, DELETE)
- Test error cases (404, 400, 403)
- Use fixtures for common setup
- Mock external API calls
- Aim for 80%+ code coverage

---

## Deployment

### Local Deployment with Docker

```bash
# Build and run
docker-compose up

# Access at http://localhost:5000
```

### Production Deployment with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app

# For production, use a reverse proxy (nginx) in front
```

### Deploy to Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set OPENAI_API_KEY=your-key
# ... set other variables ...

# Deploy
git push heroku main

# View logs
heroku logs -t
```

### Deploy to AWS

1. Create EC2 instance (Ubuntu 20.04)
2. Install Python and PostgreSQL
3. Clone repository
4. Set up virtual environment
5. Install dependencies
6. Use Gunicorn + Nginx
7. Configure SSL with Let's Encrypt

---

## Troubleshooting

### Common Issues

**1. Database not found**

```bash
# Reinitialize database
python
>>> from app import create_app
>>> from database.db import init_db
>>> app = create_app()
>>> with app.app_context():
...     init_db()
```

**2. Import errors**

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**3. Port 5000 already in use**

```bash
# Change port in run.py or environment variable
FLASK_RUN_PORT=5001 python run.py
```

**4. API key errors**

- Check `.env` file has correct API keys
- Verify API keys are valid on provider websites
- Check API rate limits haven't been exceeded

**5. CORS errors**

- Ensure Flask-CORS is installed
- Check CORS configuration in `app.py`
- May need to adjust allowed origins for production

### Debug Mode

Enable detailed debugging:

```bash
# In .env
FLASK_DEBUG=True
FLASK_ENV=development

# Or in Python
python
>>> from app import create_app
>>> app = create_app('development')
>>> app.run(debug=True)
```

### Check Logs

```bash
# View application logs
tail -f logs/intellivault.log

# View Docker logs
docker-compose logs -f web

# View Heroku logs
heroku logs -t
```

---

## Next Steps

1. **Complete PDF Processing**: Finish implementing `routes/pdf.py`
2. **Implement AI Features**: Complete `ai/` modules
3. **Add Frontend JavaScript**: Implement `static/js/` files
4. **Create Additional Templates**: Build remaining HTML templates
5. **Set Up Vector Database**: Implement FAISS integration
6. **Write Comprehensive Tests**: Increase test coverage
7. **Deploy to Production**: Choose hosting platform
8. **Monitor and Optimize**: Set up logging and performance monitoring

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated**: 2024
**Version**: 1.0.0
