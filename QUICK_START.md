# IntelliVault - Quick Start Guide

Get IntelliVault up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Git
- 100MB disk space

## Step 1: Setup (1 minute)

```bash
# Clone/Open project
cd Intellivault

# Create virtual environment
python -m venv venv

# Activate it
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys (optional, app works without them initially)
```

## Step 3: Run (1 minute)

```bash
python run.py
```

Open browser: **http://localhost:5000**

## Step 4: Login (1 minute)

**Demo Account:**
- Username: `demouser`
- Password: `demo123`

## Step 5: Explore (1 minute)

- ✅ Dashboard: See your statistics
- ✅ Notes: Create and manage notes
- ✅ Upload: Upload PDF documents (when PDF processing is implemented)
- ✅ Search: Search across your documents
- ✅ Settings: Customize your experience

---

## API Keys (Optional)

For AI features, add these to `.env`:

```
OPENAI_API_KEY=sk-... (from https://platform.openai.com)
HUGGINGFACE_API_KEY=hf_... (from https://huggingface.co)
```

---

## Common Commands

```bash
# Run development server
python run.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=.

# Format code
black .

# Check style
flake8 .

# Run with Docker
docker-compose up

# Database commands
python
>>> from app import create_app
>>> from database.db import init_db, seed_db
>>> app = create_app()
>>> with app.app_context():
...     init_db()      # Create tables
...     seed_db()      # Add demo data
```

---

## Project Structure

```
Intellivault/
├── routes/           # Web endpoints
├── database/         # Database models
├── ai/              # AI features (to implement)
├── utils/           # Helper functions
├── templates/       # HTML pages
├── static/          # CSS, JavaScript, Images
├── app.py           # Flask app factory
├── config.py        # Configuration
└── run.py           # Development server
```

---

## What's Included

✅ **Complete Backend**
- User authentication (register, login, password reset)
- Database models (User, Document, Note, Quiz, Chat)
- RESTful API endpoints
- Error handling and logging

✅ **Frontend UI**
- Responsive Bootstrap 5 templates
- Gradient design with modern styling
- Dashboard with statistics
- Notes management interface

✅ **Configuration**
- Multiple environments (development, testing, production)
- Environment variable management
- Security headers (CSRF, CORS)

✅ **Deployment Ready**
- Dockerfile for containerization
- docker-compose for local development
- Procfile for Heroku
- WSGI entry point for Gunicorn

---

## What's Next

1. **PDF Processing**: Upload and extract text from PDFs
2. **AI Features**: Document summarization, Q&A, keyword extraction
3. **Quiz Generation**: Auto-generate quizzes from documents
4. **Vector Search**: Semantic search using embeddings
5. **Chat Interface**: AI chatbot for document Q&A

See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for detailed instructions.

---

## Troubleshooting

**Port 5000 in use?**
```bash
FLASK_RUN_PORT=5001 python run.py
```

**Dependencies not installing?**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Database errors?**
```bash
# Reset database
rm intellivault.db
python run.py
```

**Need help?**
See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) Troubleshooting section.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 2.3.3 |
| **Database** | SQLAlchemy + SQLite/PostgreSQL |
| **Auth** | Flask-Login + bcrypt |
| **Frontend** | Bootstrap 5 + JavaScript |
| **AI** | OpenAI + Sentence-Transformers + LangChain |
| **Deployment** | Docker + Gunicorn + Nginx |

---

**Happy coding! 🚀**

Questions? Check [README.md](README.md) or [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
