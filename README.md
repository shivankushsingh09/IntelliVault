# IntelliVault - Intelligent Note-Taking & Document Management System

IntelliVault is a powerful Flask-based web application that combines intelligent note-taking with AI-powered document analysis. Upload PDFs, extract insights, generate quizzes, and chat with your documents.

## Features

### 📄 Document Management
- Upload and organize PDF, DOCX, and TXT files
- Full-text search across documents
- Document tagging and categorization
- Automatic text extraction
- Vector database indexing for semantic search

### 📝 Intelligent Notes
- Create notes manually or auto-generate from documents
- Pin important notes to dashboard
- Archive old notes
- Color-coded highlights
- Tag and organize notes
- Full-text search

### 🤖 AI-Powered Features
- **Summarization**: Auto-generate concise summaries from documents
- **Keyword Extraction**: Extract key concepts and topics
- **Quiz Generation**: Create quizzes from document content
- **Document Q&A**: Chat with your documents using AI
- **Embeddings**: Semantic search using vector embeddings

### 👤 User Management
- User registration and authentication
- Profile customization
- Preference settings (theme, notifications)
- Password management
- Session tracking

### 📊 Dashboard
- Overview statistics
- Recent documents and notes
- Quick access to pinned items
- Activity tracking

## Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Flask-CORS** - Cross-origin requests

### Database
- **SQLite** (development)
- **PostgreSQL** (production)

### AI/ML
- **OpenAI GPT** - LLM for summarization and Q&A
- **Sentence Transformers** - Embeddings generation
- **LangChain** - LLM orchestration
- **FAISS** - Vector database

### Document Processing
- **PyPDF2** - PDF extraction
- **python-docx** - DOCX support
- **pdfplumber** - Advanced PDF parsing

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling
- **JavaScript** - Interactivity
- **Bootstrap** - UI Framework

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
cd IntelliVault
```

2. **Create virtual environment**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings
# Add your API keys for OpenAI, HuggingFace, etc.
```

5. **Initialize database**
```bash
python run.py
```
The application will automatically create the database tables on first run.

## Running the Application

### Development Server
```bash
python run.py
```
The application will start on `http://localhost:5000`

### Production Server (using Gunicorn)
```bash
gunicorn wsgi:app
```

## Usage

### Creating an Account
1. Go to the registration page
2. Enter username, email, password
3. Click "Register"
4. Log in with your credentials

### Uploading Documents
1. Go to Dashboard → Upload
2. Select a PDF, DOCX, or TXT file
3. Add title and description (optional)
4. Click "Upload"
5. Wait for processing to complete

### Creating Notes
1. Click "New Note"
2. Enter title and content
3. Optionally link to a document
4. Save note

### Using AI Features
1. **Summarize**: Select document → Click "Summarize"
2. **Extract Keywords**: Select document → Click "Keywords"
3. **Generate Quiz**: Select document → Click "Create Quiz"
4. **Chat with Document**: Open document → Chat panel

### Searching
Use the search bar to find documents, notes, and quizzes by keyword.

## Project Structure

```
IntelliVault/
├── app.py                      # Application factory
├── config.py                   # Configuration settings
├── run.py                      # Development server
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
│
├── database/
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy models
│   └── db.py                   # Database utilities
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Authentication routes
│   ├── dashboard.py            # Dashboard routes
│   ├── notes.py                # Notes routes
│   ├── pdf.py                  # PDF upload/view
│   ├── ai.py                   # AI features routes
│   ├── quiz.py                 # Quiz routes
│   └── profile.py              # Profile & settings
│
├── ai/
│   ├── __init__.py
│   ├── summarizer.py           # Document summarization
│   ├── keyword.py              # Keyword extraction
│   ├── chatbot.py              # AI chatbot
│   ├── embeddings.py           # Vector embeddings
│   └── quiz_generator.py       # Quiz generation
│
├── utils/
│   ├── __init__.py
│   ├── pdf_processor.py        # PDF processing
│   ├── validators.py           # Input validation
│   └── decorators.py           # Custom decorators
│
├── templates/
│   ├── base.html               # Base template
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Dashboard
│   ├── notes.html              # Notes list
│   ├── upload.html             # PDF upload
│   ├── profile.html            # User profile
│   └── settings.html           # Settings page
│
├── static/
│   ├── css/
│   │   ├── style.css           # Main stylesheet
│   │   └── responsive.css      # Responsive design
│   ├── js/
│   │   ├── main.js             # Main JavaScript
│   │   ├── notes.js            # Notes functionality
│   │   └── api.js              # API utilities
│   └── images/
│
├── uploads/                    # Uploaded files
├── vector_db/                  # Vector database
└── logs/                       # Application logs
```

## API Endpoints

### Authentication
- `POST /auth/api/register` - Register new user
- `POST /auth/api/login` - User login
- `POST /auth/api/logout` - User logout

### Dashboard
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/recent` - Get recent items
- `GET /api/search` - Search across items

### Notes
- `GET /notes/api/notes` - List all notes
- `POST /notes/api/notes` - Create note
- `GET /notes/api/notes/<id>` - Get note
- `PUT /notes/api/notes/<id>` - Update note
- `DELETE /notes/api/notes/<id>` - Delete note

### Documents
- `POST /pdf/api/upload` - Upload document
- `GET /pdf/api/documents` - List documents
- `GET /pdf/api/documents/<id>` - Get document

### AI Features
- `POST /ai/api/summarize` - Summarize document
- `POST /ai/api/chat` - Chat with document
- `POST /ai/api/keywords` - Extract keywords

### Quiz
- `GET /quiz/api/quizzes` - List quizzes
- `POST /quiz/api/quiz/<id>/submit` - Submit quiz

### Profile
- `GET /profile/api/profile` - Get user profile
- `PUT /profile/api/profile` - Update profile
- `POST /profile/api/profile/password` - Change password

## Configuration

### Database
- **Development**: SQLite (local file)
- **Production**: PostgreSQL (recommended)

Edit `config.py` to change database settings.

### API Keys
Add your API keys to `.env`:
```
OPENAI_API_KEY=your-key-here
HUGGINGFACE_API_KEY=your-key-here
```

### File Upload
Max file size: 50MB (configurable in config.py)
Allowed formats: PDF, DOCX, TXT

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8 .
```

### Database Migrations (if using Alembic)
```bash
flask db upgrade
```

## Deployment

### Using Gunicorn + Nginx
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
```

### Using Docker
```bash
docker build -t intellivault .
docker run -p 5000:5000 intellivault
```

### Cloud Deployment
- **Heroku**: Use `Procfile` and deploy with `git push heroku main`
- **AWS**: Use EB CLI or run on EC2
- **Google Cloud**: Deploy with `gcloud app deploy`

## Security

- Passwords are hashed with bcrypt
- CSRF protection enabled
- SQL injection prevention with SQLAlchemy
- XSS protection with Werkzeug
- CORS configured appropriately
- HTTPS recommended for production

## Performance Tips

1. Enable vector database indexing for large document collections
2. Use caching for frequently accessed documents
3. Optimize database queries
4. Enable gzip compression in Nginx
5. Use CDN for static files

## Troubleshooting

### Database Connection Error
- Check DATABASE_URL in .env
- Ensure database server is running
- Verify credentials

### PDF Upload Fails
- Check file size (max 50MB)
- Verify file format (PDF, DOCX, TXT)
- Check disk space

### AI Features Not Working
- Verify API keys in .env
- Check API rate limits
- Ensure internet connection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review code comments

## Roadmap

- [ ] Mobile app
- [ ] Real-time collaboration
- [ ] Advanced analytics
- [ ] Integration with cloud storage
- [ ] Plugin system
- [ ] Multi-language support

## Changelog

### Version 1.0.0
- Initial release
- Core features implemented
- AI integration
- User authentication

---

**Built with ❤️ using Flask and AI**

Last Updated: 2024
