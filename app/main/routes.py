#!/usr/bin/env python3
"""Routes for the Flask application."""
from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm, EmptyForm, SearchForm
from app.models import (
    User,
    CalendarEvent,
)  # Planner, Resource, Contact, Communication  # Import of all required models
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
@login_required
def dashboard():
    """Dashboard page with dynamic sections."""

    # Flash a welcome message for first-time visits
    if request.method == "GET" and not g.get("visited_dashboard", False):
        flash(_("Welcome to your dashboard, {}!").format(current_user.username))
        g.visited_dashboard = True  # Use Flask session for persistence if needed

    # Fetch planner events
    planner_events = db.session.scalars(
        sa.select(Planner).where(Planner.user_id == current_user.id)
    ).all()

    # Fetch resources (photos and documents)
    photo_gallery = db.session.scalars(
        sa.select(Resource).where(
            Resource.user_id == current_user.id, Resource.resource_type == "photo"
        )
    ).all()

    documents = db.session.scalars(
        sa.select(Resource).where(
            Resource.user_id == current_user.id, Resource.resource_type == "document"
        )
    ).all()

    # Fetch user's contacts
    contacts = db.session.scalars(
        sa.select(Contact).where(Contact.user_id == current_user.id)
    ).all()

    # Fetch recent communications (sent and received)
    communications_sent = db.session.scalars(
        sa.select(Communication)
        .where(Communication.sender_id == current_user.id)
        .order_by(Communication.timestamp.desc())
    ).all()

    communications_received = db.session.scalars(
        sa.select(Communication)
        .where(Communication.receiver_id == current_user.id)
        .order_by(Communication.timestamp.desc())
    ).all()

    # Determine the section to display
    section = request.args.get("section", "welcome")

    # Pass data to the template for rendering
    return render_template(
        "dashboard.html",
        title=_("Dashboard"),
        section=section,
        planner_events=planner_events,
        photo_gallery=photo_gallery,
        documents=documents,
        contacts=contacts,
        communications_sent=communications_sent,
        communications_received=communications_received,
    )


@bp.route("/dashboard/planner")
@login_required
def planner():
    # Fetch the user's calendar events
    events = current_user.calendar_events.order_by(CalendarEvent.start_time).all()

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
    return render_template("planner.html", title="Planner", events=event_data)


@bp.route("/search")
@login_required
def search():
    form = SearchForm()
    if not form.validate():
        flash(_("Invalid search query"))
        return redirect(url_for("main.dashboard"))

    search_query = form.q.data
    page = request.args.get("page", 1, type=int)  # Get current page number
    per_page = 5  # Number of results per page

    # Query the database for content matching the search query
    results_query = db.session.query(ContentModel).filter(
        ContentModel.title.ilike(f"%{search_query}%"),
        ContentModel.user_id == current_user.id,
    )
    paginated_results = results_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "search_results.html",
        title=_("Search Results"),
        results=paginated_results.items,  # Results for the current page
        pagination=paginated_results,  # Pagination metadata
    )


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title=_("Edit Profile"), form=form)
