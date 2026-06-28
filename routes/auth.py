"""
Authentication Routes
Handles user registration, login, logout, and password management
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from database.models import db, User
from datetime import datetime
import re
from itsdangerous import URLSafeTimedSerializer

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        errors = []
        
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        elif User.query.filter_by(username=username).first():
            errors.append("Username already exists")
        
        if not email:
            errors.append("Email is required")
        elif not validate_email(email):
            errors.append("Invalid email format")
        elif User.query.filter_by(email=email).first():
            errors.append("Email already registered")
        
        if not password:
            errors.append("Password is required")
        else:
            valid, msg = validate_password(password)
            if not valid:
                errors.append(msg)
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name or username
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username_or_email or not password:
            flash('Username/Email and password are required', 'danger')
            return render_template('login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email.lower())
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is deactivated', 'danger')
                return render_template('login.html')
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('auth.login'))


def generate_reset_token(email, secret_key):
    """Generate a timed password reset token"""
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='password-reset-salt')


def verify_reset_token(token, secret_key, expiration=3600):
    """Verify password reset token"""
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
        return email
    except Exception:
        return None


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        token = None
        reset_url = None
        
        if user:
            token = generate_reset_token(user.email, current_app.config['SECRET_KEY'])
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            print(f"\n[DEMO MODE PASSWORD RESET LINK]: {reset_url}\n")
            
        return render_template('forgot_password_success.html', reset_url=reset_url, email=email)
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    email = verify_reset_token(token, current_app.config['SECRET_KEY'])
    if not email:
        flash('The password reset link is invalid or has expired', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', token=token)
        
        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'danger')
            return render_template('reset_password.html', token=token)
        
        # Update user password
        user.set_password(password)
        db.session.commit()
        
        flash('Password reset successfully. Please log in with your new password', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)


# API Routes

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    
    # Validation
    errors = []
    
    if not username or len(username) < 3:
        errors.append("Invalid username")
    
    if not email or not validate_email(email):
        errors.append("Invalid email")
    
    if not password:
        errors.append("Invalid password")
    else:
        valid, msg = validate_password(password)
        if not valid:
            errors.append(msg)
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        username=username,
        email=email,
        full_name=full_name or username
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username_or_email = data.get('username_or_email', '').strip()
    password = data.get('password', '')
    
    if not username_or_email or not password:
        return jsonify({'error': 'Username/Email and password required'}), 400
    
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email.lower())
    ).first()
    
    if user and user.check_password(password):
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=True)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for logout"""
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/api/user/profile', methods=['GET'])
@login_required
def api_get_profile():
    """Get current user profile"""
    return jsonify(current_user.to_dict()), 200
