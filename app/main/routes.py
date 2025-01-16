#!/usr/bin/env python3
"""Routes for the Flask application."""
from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask import session, request, jsonify
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm, EmptyForm, SearchForm
from app.models import (
    User,
    CalendarEvent,
    # ContentModel,
)
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    """ Landing Page for a standalone application for login to application"""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page with dynamic sections."""

    if request.method == "GET" and not session.get("visited_dashboard", False):
        flash(_("Welcome to your dashboard, {}!").format(current_user.username))
        session["visited_dashboard"] = True

    # Fetch calendar events
    calendarevents = db.session.scalars(
        sa.select(CalendarEvent).where(CalendarEvent.user_id == current_user.id)
    ).all()

    # Determine the section to display
    section = request.args.get("section", "welcome")

    # Pass data to the template for rendering
    return render_template(
        "dashboard.html",
        title=_("Dashboard"),
        section=section,
        calendarevents=calendarevents
    )

@bp.route("/dashboard/home")
@login_required     
def dashboard_home():
    pass
    
@bp.route("/dashboard/planner")
@login_required    
def dashboard_planner():
    pass
    
@bp.route("/dashboard/calendarevents")
@login_required
def calendarevents():
    # Fetch the user's calendar events
    events = current_user.calendarevents.order_by(CalendarEvent.start_time).all()

    # Prepare events data for rendering
    event_data = [
        {
            "title": event.title,
            "description": event.description,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat(),
        }
        for event in events
    ]

    # Render the calendar page and pass the events
    return render_template(
        "calendar_events.html", title="CalendarEvent", events=event_data
    )


@bp.route("/dashboard/edit_profile", methods=["GET", "POST"])
@login_required
def editprofile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes have been saved."), "success")
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template(
        "edit_profile.html",
        title=_("Edit Profile"),
        form=form,
    )

@bp.route('/dashboard/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)


@bp.route("/dashboard/search")
@login_required
def search():
    form = SearchForm()
    if not form.validate():
        for field, errors in form.errors.items():
            for error in errors:
                flash(_("Error in the {} field: {}").format(field, error), "danger")
        return redirect(url_for("main.dashboard"))

    search_query = form.q.data
    page = request.args.get("page", 1, type=int)  # Get current page number
    per_page = 5  # Number of results per page

    # Query the database for content matching the search query
    results_query = db.session.query(ContentModel).filter(
        ContentModel.title.ilike(f"%{search_query}%"),
        ContentModel.user_id == current_user.id,
    )

    if not results_query:
        flash(
            _("No results found for your search query: {}").format(search_query),
            "warning",
        )
        return redirect(url_for("main.dashboard"))

    paginated_results = results_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    if not paginated_results.items:
        flash(_("No results found on this page."), "warning")
        return redirect(url_for("main.dashboard"))

    return render_template(
        "search_results.html",
        title=_("Search Results"),
        results=paginated_results.items,  # Results for the current page
        pagination=paginated_results,  # Pagination metadata
    )

@bp.route("/logout")
def logout():
    """Logs out the user and redirects to the login page."""
    logout_user()
    flash(_("You have been logged out."))
    return redirect(url_for("auth.login"))
