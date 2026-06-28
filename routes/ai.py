"""AI Routes"""
import re
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from database.models import db, Document, Note, ChatSession, ChatMessage
from sqlalchemy import desc

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


def clean_text_snippet(text: str, query: str, length: int = 320) -> str:
    if not text:
        return ''
    text = ' '.join(text.split())
    idx = text.lower().find(query.lower())
    if idx >= 0:
        start = max(0, idx - 80)
        end = min(len(text), idx + length)
        snippet = text[start:end].strip()
        if start > 0:
            snippet = '...' + snippet
        if end < len(text):
            snippet = snippet + '...'
        return snippet
    return text[:length].strip() + ('...' if len(text) > length else '')


def extractive_summary(text: str, sentence_count: int = 5) -> str:
    text = ' '.join(text.split())
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= sentence_count:
        return text
    summary = ' '.join(sentences[:sentence_count])
    return summary.strip()


def generate_document_summary(text: str) -> str:
    text = (text or '').strip()
    if not text:
        return 'No document text available to summarize.'

    if current_app.config.get('OPENAI_API_KEY'):
        try:
            import openai
            openai.api_key = current_app.config['OPENAI_API_KEY']
            prompt = (
                'Summarize the following document content into 4 concise bullet points:\n\n'
                f'{text[:10000]}'
            )
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=250,
                temperature=0.6,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    return extractive_summary(text)


def build_ai_response(user, prompt):
    """Create a response using uploaded documents and notes."""
    prompt_text = (prompt or '').strip()
    if not prompt_text:
        return "Ask a question about your documents or notes and I will help you find the right information."

    documents = Document.query.filter_by(user_id=user.id).all()
    notes = Note.query.filter_by(user_id=user.id).all()
    query_lower = prompt_text.lower()

    hits = []
    for document in documents:
        searchable = ' '.join(filter(None, [document.title, document.description, document.text_content]))
        if query_lower in searchable.lower():
            snippet = clean_text_snippet(document.text_content or document.description or '', prompt_text)
            hits.append(f"Document '{document.title}': {snippet}")

    for note in notes:
        searchable = ' '.join(filter(None, [note.title, note.content]))
        if query_lower in searchable.lower():
            snippet = clean_text_snippet(note.content, prompt_text)
            hits.append(f"Note '{note.title}': {snippet}")

    if hits:
        return 'Here are the most relevant results from your vault:\n\n' + '\n\n'.join(hits[:5])

    if 'document' in query_lower or 'file' in query_lower or 'pdf' in query_lower:
        if documents:
            titles = ', '.join([doc.title for doc in documents[:5]])
            return f"You have {len(documents)} documents. Recent documents: {titles}."
        return "You do not have any uploaded documents yet. Use the Upload page to add your first file."

    if 'note' in query_lower:
        if notes:
            titles = ', '.join([note.title for note in notes[:5]])
            return f"You have {len(notes)} notes. Recent notes: {titles}."
        return "You do not have any notes yet. Create one from the Notes page."

    return (
        "I can help you explore your uploaded documents, review notes, and answer questions about your content. "
        "Try asking about a document title, note topic, or say 'show my documents'."
    )


@ai_bp.route('/chat')
@login_required
def chat():
    new_session = request.args.get('new', type=int)
    chat_session = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).order_by(desc(ChatSession.updated_at)).first()
    if new_session or not chat_session:
        if chat_session:
            chat_session.is_active = False
            db.session.add(chat_session)
        chat_session = ChatSession(
            user_id=current_user.id,
            title=f"AI Chat Session {datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )
        db.session.add(chat_session)
        db.session.commit()

    messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.created_at).all()
    return render_template('chat.html', session=chat_session, messages=messages)


@ai_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}
    message_text = (data.get('message') or '').strip()
    session_id = data.get('session_id')

    if not message_text:
        return jsonify({'error': 'Message is required'}), 400

    chat_session = None
    if session_id:
        chat_session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not chat_session:
        chat_session = ChatSession(
            user_id=current_user.id,
            title=f"AI Chat Session {datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )
        db.session.add(chat_session)
        db.session.commit()

    user_message = ChatMessage(session_id=chat_session.id, role='user', content=message_text)
    db.session.add(user_message)
    response_text = build_ai_response(current_user, message_text)
    assistant_message = ChatMessage(session_id=chat_session.id, role='assistant', content=response_text)
    chat_session.updated_at = datetime.utcnow()
    db.session.add(assistant_message)
    db.session.add(chat_session)
    db.session.commit()

    return jsonify({
        'response': response_text,
        'session_id': chat_session.id,
        'session_title': chat_session.title
    }), 200


@ai_bp.route('/summarize', methods=['GET', 'POST'])
@login_required
def summarize():
    documents = Document.query.filter_by(user_id=current_user.id, status='completed').all()
    summary = None
    selected_document = None
    error = None

    if request.method == 'POST':
        document_id = request.form.get('document_id', type=int)
        selected_document = Document.query.filter_by(id=document_id, user_id=current_user.id, status='completed').first()
        if not selected_document:
            error = 'Please select a valid completed document.'
        else:
            source_text = selected_document.text_content or selected_document.description or ''
            if not source_text.strip():
                error = 'The selected document has no text to summarize.'
            else:
                summary = generate_document_summary(source_text)

    return render_template(
        'summarize.html',
        documents=documents,
        summary=summary,
        selected_document=selected_document,
        error=error
    )
