"""Notes Routes"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import db, Note, Document
from sqlalchemy import desc

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')


@notes_bp.route('/')
@login_required
def list_notes():
    """List all user notes"""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')  # all, pinned, archived
    
    query = Note.query.filter_by(user_id=current_user.id)
    
    if filter_type == 'pinned':
        query = query.filter_by(is_pinned=True, is_archived=False)
    elif filter_type == 'archived':
        query = query.filter_by(is_archived=True)
    else:
        query = query.filter_by(is_archived=False)
    
    notes = query.order_by(desc(Note.created_at)).paginate(page=page, per_page=10)
    return render_template('notes.html', notes=notes.items, pagination=notes)


@notes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_note():
    """Create a new note"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        doc_id = request.form.get('document_id')
        
        if not title or not content:
            return render_template('note_form.html', error='Title and content required')
        
        note = Note(
            user_id=current_user.id,
            title=title,
            content=content,
            document_id=doc_id if doc_id else None,
        )
        
        db.session.add(note)
        db.session.commit()
        
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    return render_template('note_form.html', note=None, action='Create Note')


@notes_bp.route('/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Edit an existing note"""
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return "Unauthorized", 403

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            return render_template('note_form.html', note=note, action='Update Note', error='Title and content are required.')

        note.title = title
        note.content = content
        db.session.commit()

        flash('Note updated successfully.', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))

    return render_template('note_form.html', note=note, action='Update Note')


@notes_bp.route('/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully.', 'success')
    return redirect(url_for('notes.list_notes'))


@notes_bp.route('/<int:note_id>')
@login_required
def view_note(note_id):
    """View a specific note"""
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return "Unauthorized", 403
    return render_template('note_detail.html', note=note)


# API Routes

@notes_bp.route('/api/notes', methods=['GET'])
@login_required
def api_list_notes():
    """Get all notes for user"""
    filter_type = request.args.get('filter', 'all')
    limit = request.args.get('limit', 50, type=int)
    
    query = Note.query.filter_by(user_id=current_user.id)
    
    if filter_type == 'pinned':
        query = query.filter_by(is_pinned=True, is_archived=False)
    elif filter_type == 'archived':
        query = query.filter_by(is_archived=True)
    else:
        query = query.filter_by(is_archived=False)
    
    notes = query.order_by(desc(Note.created_at)).limit(limit).all()
    return jsonify([n.to_dict() for n in notes]), 200


@notes_bp.route('/api/notes', methods=['POST'])
@login_required
def api_create_note():
    """Create a new note via API"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    doc_id = data.get('document_id')
    
    if not title or not content:
        return jsonify({'error': 'Title and content required'}), 400
    
    note = Note(
        user_id=current_user.id,
        title=title,
        content=content,
        document_id=doc_id if doc_id else None,
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201


@notes_bp.route('/api/notes/<int:note_id>', methods=['GET'])
@login_required
def api_get_note(note_id):
    """Get a specific note"""
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(note.to_dict()), 200


@notes_bp.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def api_update_note(note_id):
    """Update a note"""
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    note.is_pinned = data.get('is_pinned', note.is_pinned)
    note.is_archived = data.get('is_archived', note.is_archived)
    
    db.session.commit()
    return jsonify(note.to_dict()), 200


@notes_bp.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def api_delete_note(note_id):
    """Delete a note"""
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({'message': 'Note deleted'}), 200
