"""Profile and Settings Routes"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from database.models import db, User

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@profile_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)


@profile_bp.route('/api/profile', methods=['GET'])
@login_required
def api_get_profile():
    return jsonify(current_user.to_dict()), 200


@profile_bp.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    current_user.full_name = data.get('full_name', current_user.full_name)
    current_user.bio = data.get('bio', current_user.bio)
    current_user.theme = data.get('theme', current_user.theme)
    current_user.notifications_enabled = data.get('notifications_enabled', current_user.notifications_enabled)
    
    db.session.commit()
    return jsonify(current_user.to_dict()), 200


@profile_bp.route('/api/profile/reset', methods=['POST'])
@login_required
def api_reset_profile():
    current_user.theme = 'light'
    current_user.notifications_enabled = True
    db.session.commit()
    return jsonify(current_user.to_dict()), 200


@profile_bp.route('/api/profile/delete', methods=['DELETE'])
@login_required
def api_delete_profile():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Account deleted'}), 200


@profile_bp.route('/api/profile/password', methods=['POST'])
@login_required
def api_change_password():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not current_user.check_password(old_password):
        return jsonify({'error': 'Invalid current password'}), 400
    
    if len(new_password) < 8:
        return jsonify({'error': 'Password too short'}), 400
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed'}), 200
