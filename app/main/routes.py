#!/usr/bin/env python3
"""Routes for the Flask application."""
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required, login_user, logout_user
from app.main.forms import LoginForm, RegisterForm, EditProfileForm, EmptyForm
from app.main import bp
from app.models import User
from app import db
from flask_babel import _
import sqlalchemy as sa  # For SQLAlchemy core

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """Home/Dashboard page."""
    return render_template('index.html', title=_('Home'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Logic to authenticate user
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), 'error')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        flash(_('Logged in successfully!'))
        return redirect(url_for('main.index'))
    
    return render_template('login.html', title=_('Login'), form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Logic to register user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Registration successful!'))
        return redirect(url_for('main.login'))
        
    return render_template('register.html', title=_('Register'), form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit profile page."""
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@bp.route('/resources')
def resources():
    """Placeholder for resources."""
    return _("Resources page (to be implemented)")

@bp.route('/planner')
def planner():
    """Placeholder for planner."""
    return _("Planner page (to be implemented)")

@bp.route('/compose')
def compose():
    """Placeholder for compose."""
    return _("Compose page (to be implemented)")

@bp.route('/logout')
def logout():
    """Logout the current user."""
    logout_user()
    flash(_('You have been logged out.'))
    return redirect(url_for('main.index'))
