"""Quiz Routes"""
import json
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from database.models import db, Document, Quiz, QuizAttempt

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_bp.route('/')
@login_required
def list_quizzes():
    documents = Document.query.filter_by(user_id=current_user.id, status='completed').all()
    quizzes = Quiz.query.filter_by(user_id=current_user.id).order_by(Quiz.created_at.desc()).all()
    return render_template('quizzes.html', documents=documents, quizzes=quizzes)


@quiz_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_quiz():
    documents = Document.query.filter_by(user_id=current_user.id, status='completed').all()
    quizzes = Quiz.query.filter_by(user_id=current_user.id).order_by(Quiz.created_at.desc()).all()

    if request.method == 'POST':
        document_id = request.form.get('document_id', type=int)
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        question_count = request.form.get('question_count', 5, type=int)

        document = Document.query.filter_by(id=document_id, user_id=current_user.id).first()
        if not document:
            return render_template(
                'quizzes.html',
                documents=documents,
                quizzes=quizzes,
                error='Please select a valid document.'
            )

        questions = []
        for i in range(1, question_count + 1):
            questions.append({
                'id': i,
                'question': f"Question {i} from '{document.title}'",
                'options': [
                    'Answer option A',
                    'Answer option B',
                    'Answer option C',
                    'Answer option D'
                ],
                'correct': 0
            })

        quiz = Quiz(
            user_id=current_user.id,
            document_id=document.id,
            title=title or f"Quiz for {document.title}",
            description=description or f"Quiz generated from document {document.title}",
            question_count=len(questions),
            difficulty='medium',
        )
        quiz.set_questions(questions)
        db.session.add(quiz)
        db.session.commit()

        return redirect(url_for('quiz.take_quiz', quiz_id=quiz.id))

    return render_template('quizzes.html', documents=documents, quizzes=quizzes)


@quiz_bp.route('/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_id != current_user.id:
        return "Unauthorized", 403
    questions = quiz.get_questions()
    return render_template('quiz_take.html', quiz=quiz, questions=questions)


@quiz_bp.route('/api/quizzes', methods=['GET'])
@login_required
def api_list_quizzes():
    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    return jsonify([q.to_dict() for q in quizzes]), 200


@quiz_bp.route('/api/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def api_submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    answers = request.get_json(silent=True) or {}
    questions = quiz.get_questions()
    correct = 0

    for q in questions:
        selected = answers.get(str(q['id']))
        if selected is not None and int(selected) == int(q.get('correct', -1)):
            correct += 1

    score = round((correct / len(questions)) * 100, 2) if questions else 0
    quiz.attempts_count = (quiz.attempts_count or 0) + 1
    quiz.best_score = max(quiz.best_score or 0, score)
    db.session.add(quiz)

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        responses_data=json.dumps(answers),
        score=score,
        correct_answers=correct,
        total_questions=len(questions),
        time_spent_seconds=0
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify({'score': score, 'correct': correct, 'total': len(questions)}), 200
