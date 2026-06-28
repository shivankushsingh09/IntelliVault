"""
Dashboard Routes
Main dashboard and overview pages
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from database.models import db, Document, Note, Quiz, ChatSession
from sqlalchemy import desc, or_

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get user statistics
    documents_count = Document.query.filter_by(user_id=current_user.id).count()
    notes_count = Note.query.filter_by(user_id=current_user.id).count()
    quizzes_count = Quiz.query.filter_by(user_id=current_user.id).count()
    chat_sessions_count = ChatSession.query.filter_by(user_id=current_user.id).count()
    
    # Get recent documents
    recent_documents = Document.query.filter_by(user_id=current_user.id).order_by(
        desc(Document.created_at)
    ).limit(5).all()
    
    # Get pinned notes
    pinned_notes = Note.query.filter_by(
        user_id=current_user.id,
        is_pinned=True,
        is_archived=False
    ).order_by(desc(Note.updated_at)).limit(5).all()
    
    # Get recent notes (paginated)
    notes_pagination = Note.query.filter_by(
        user_id=current_user.id,
        is_archived=False
    ).order_by(desc(Note.created_at)).paginate(page=page, per_page=per_page)
    
    stats = {
        'documents': documents_count,
        'notes': notes_count,
        'quizzes': quizzes_count,
        'chat_sessions': chat_sessions_count,
        'total_items': documents_count + notes_count + quizzes_count,
    }
    
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_documents=recent_documents,
        pinned_notes=pinned_notes,
        notes=notes_pagination.items,
        pagination=notes_pagination
    )


@dashboard_bp.route('/search')
@login_required
def search():
    """Search across documents and notes"""
    query = request.args.get('q', '', type=str).strip()
    search_type = request.args.get('type', 'all', type=str)  # all, documents, notes, quizzes
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if not query or len(query) < 2:
        return render_template('search.html', query=query, results=None, message='Query too short')
    
    results = {'documents': [], 'notes': [], 'quizzes': []}
    
    # Search documents
    if search_type in ['all', 'documents']:
        docs = Document.query.filter_by(user_id=current_user.id).filter(
            or_(
                Document.title.ilike(f'%{query}%'),
                Document.description.ilike(f'%{query}%'),
                Document.tags.ilike(f'%{query}%'),
                Document.text_content.ilike(f'%{query}%')
            )
        ).order_by(desc(Document.created_at)).limit(20).all()
        results['documents'] = docs
    
    # Search notes
    if search_type in ['all', 'notes']:
        notes = Note.query.filter_by(user_id=current_user.id).filter(
            or_(
                Note.title.ilike(f'%{query}%'),
                Note.content.ilike(f'%{query}%'),
                Note.tags.ilike(f'%{query}%')
            )
        ).order_by(desc(Note.created_at)).limit(20).all()
        results['notes'] = notes
    
    # Search quizzes
    if search_type in ['all', 'quizzes']:
        quizzes = Quiz.query.filter_by(user_id=current_user.id).filter(
            (Quiz.title.ilike(f'%{query}%')) |
            (Quiz.description.ilike(f'%{query}%'))
        ).order_by(desc(Quiz.created_at)).limit(20).all()
        results['quizzes'] = quizzes
    
    total_results = len(results['documents']) + len(results['notes']) + len(results['quizzes'])
    
    return render_template(
        'search.html',
        query=query,
        results=results,
        total_results=total_results,
        search_type=search_type
    )


# API Routes

@dashboard_bp.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    """Get dashboard statistics"""
    documents_count = Document.query.filter_by(user_id=current_user.id).count()
    notes_count = Note.query.filter_by(user_id=current_user.id).count()
    quizzes_count = Quiz.query.filter_by(user_id=current_user.id).count()
    chat_sessions_count = ChatSession.query.filter_by(user_id=current_user.id).count()
    
    # Get storage usage
    total_size = db.session.query(db.func.sum(Document.file_size)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    
    stats = {
        'documents': documents_count,
        'notes': notes_count,
        'quizzes': quizzes_count,
        'chat_sessions': chat_sessions_count,
        'total_storage_mb': round(total_size / (1024 * 1024), 2),
        'total_items': documents_count + notes_count + quizzes_count,
    }
    
    return jsonify(stats), 200


@dashboard_bp.route('/api/dashboard/recent')
@login_required
def api_recent_items():
    """Get recently accessed/modified items"""
    limit = request.args.get('limit', 10, type=int)
    
    recent_docs = Document.query.filter_by(user_id=current_user.id).order_by(
        desc(Document.updated_at)
    ).limit(limit).all()
    
    recent_notes = Note.query.filter_by(user_id=current_user.id).order_by(
        desc(Note.updated_at)
    ).limit(limit).all()
    
    recent_quizzes = Quiz.query.filter_by(user_id=current_user.id).order_by(
        desc(Quiz.updated_at)
    ).limit(limit).all()
    
    return jsonify({
        'documents': [d.to_dict() for d in recent_docs],
        'notes': [n.to_dict() for n in recent_notes],
        'quizzes': [q.to_dict() for q in recent_quizzes],
    }), 200


@dashboard_bp.route('/api/search')
@login_required
def api_search():
    """API search endpoint"""
    query = request.args.get('q', '', type=str).strip()
    search_type = request.args.get('type', 'all', type=str)
    limit = request.args.get('limit', 20, type=int)
    
    if not query or len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    results = {'documents': [], 'notes': [], 'quizzes': []}
    
    if search_type in ['all', 'documents']:
        docs = Document.query.filter_by(user_id=current_user.id).filter(
            or_(
                Document.title.ilike(f'%{query}%'),
                Document.description.ilike(f'%{query}%'),
                Document.tags.ilike(f'%{query}%'),
                Document.text_content.ilike(f'%{query}%')
            )
        ).order_by(desc(Document.created_at)).limit(limit).all()
        results['documents'] = [d.to_dict() for d in docs]
    
    if search_type in ['all', 'notes']:
        notes = Note.query.filter_by(user_id=current_user.id).filter(
            or_(
                Note.title.ilike(f'%{query}%'),
                Note.content.ilike(f'%{query}%'),
                Note.tags.ilike(f'%{query}%')
            )
        ).order_by(desc(Note.created_at)).limit(limit).all()
        results['notes'] = [n.to_dict() for n in notes]
    
    if search_type in ['all', 'quizzes']:
        quizzes = Quiz.query.filter_by(user_id=current_user.id).filter(
            Quiz.title.ilike(f'%{query}%')
        ).order_by(desc(Quiz.created_at)).limit(limit).all()
        results['quizzes'] = [q.to_dict() for q in quizzes]
    
    return jsonify(results), 200
