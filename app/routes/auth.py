from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
import re

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        role = request.form.get('role')
        location = (request.form.get('location') or '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        # Validation
        if not name or not email or not mobile or not password or not role:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if role in ['dealer', 'service_provider'] and not location:
            flash('Location is required for dealers and service providers.', 'danger')
            return redirect(url_for('auth.register'))
            
        if role not in ['user', 'dealer', 'service_provider']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Email pattern validation
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('auth.register'))

        latitude_value = None
        longitude_value = None
        if latitude not in (None, '') and longitude not in (None, ''):
            try:
                latitude_value = float(latitude)
                longitude_value = float(longitude)
            except (TypeError, ValueError):
                flash('Invalid location coordinates.', 'danger')
                return redirect(url_for('auth.register'))

            if not (-90 <= latitude_value <= 90 and -180 <= longitude_value <= 180):
                flash('Location coordinates are out of range.', 'danger')
                return redirect(url_for('auth.register'))
            
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
            
        new_user = User(
            name=name,
            email=email,
            mobile=mobile,
            location=location or None,
            latitude=latitude_value,
            longitude=longitude_value,
            role=role,
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            # Redirect to appropriate dashboard based on role
            return redirect(url_for('dashboards.index'))
            
        flash('Invalid email or password.', 'danger')
        
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
