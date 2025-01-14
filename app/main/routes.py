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
    Resource,
    Contact,
    Communication,
    Contact,
    # ContentModel,
)
from app.main import bp
from app.services.resource_service import ResourceService


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

    if request.method == "GET" and not session.get("visited_dashboard", False):
        flash(_("Welcome to your dashboard, {}!").format(current_user.username))
        session["visited_dashboard"] = True

    # Fetch calendar events
    calendar_events = db.session.scalars(
        sa.select(CalendarEvent).where(CalendarEvent.user_id == current_user.id)
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
        calendar_events=calendar_events,
        photo_gallery=photo_gallery,
        documents=documents,
        contacts=contacts,
        communications_sent=communications_sent,
        communications_received=communications_received,
    )


@bp.route("/dashboard/calendar_events")
@login_required
def calendar_events():
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
    return render_template(
        "calendar_events.html", title="CalendarEvent", events=event_data
    )


@bp.route("/dashboard/resources", methods=["POST"])
@login_required
def create_resource():
    """Handle creating a new resource."""
    data = request.get_json()
    image = request.files.get("image").read() if "image" in request.files else None

    try:
        # Validate input data
        if Resource.validate_data(data):
            resource = ResourceService.create_resource(data, image)
            return jsonify(resource.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred."}), 500


@bp.route("/dashboard/resources/<int:resource_id>", methods=["GET"])
@login_required
def get_resource(resource_id):
    """Retrieve a resource by ID."""
    try:
        resource = ResourceService.get_resource(resource_id)
        if not resource:
            return jsonify({"error": "Resource not found."}), 404
        return jsonify(resource), 200
    except Exception as e:
        return jsonify({"error": "An error occurred."}), 500


from datetime import datetime


@bp.route("/dashboard/contact", methods=["GET"])
@login_required
def dashboard_contact():
    """Retrieve and display the contact list of staff and organizations."""
    contacts = Contact.query.all()
    contact_list = [
        {
            "id": contact.id,
            "name": contact.name,
            "phone": contact.phone,
            "email": contact.email,
            "organization": contact.organization,
            "department": contact.department,
        }
        for contact in contacts
    ]
    return jsonify(
        contact_list
    )  # You can replace with `render_template` for an HTML response


@bp.route("/dashboard/communicate", methods=["GET"])
@login_required
def dashboard_communicate():
    """Retrieve and display communication with contacts."""
    communications = Communication.query.all()
    communication_list = [
        {
            "id": communication.id,
            "contact_name": communication.contact.name,
            "message_type": communication.message_type,
            "content": communication.content,
            "timestamp": communication.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "organization": communication.contact.organization,
            "department": communication.contact.department,
        }
        for communication in communications
    ]
    return jsonify(
        communication_list
    )  # You can replace with `render_template` for an HTML response


@bp.route("/dashboard/communicate/upload", methods=["POST"])
@login_required
def upload_attachment():
    """Upload an attachment for a specific communication."""
    if "file" not in request.files or "communication_id" not in request.form:
        return jsonify({"error": "File and communication_id are required"}), 400

    file = request.files["file"]
    communication_id = request.form["communication_id"]

    if file and allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
        filename = file.filename
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Save attachment metadata to the database
        attachment = Attachment(
            communication_id=communication_id,
            filename=filename,
            filetype=file.content_type,
            filepath=filepath,
        )
        db.session.add(attachment)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "attachment": {
                        "id": attachment.id,
                        "filename": attachment.filename,
                        "filetype": attachment.filetype,
                        "filepath": attachment.filepath,
                    },
                }
            ),
            201,
        )
    else:
        return jsonify({"error": "Invalid file type"}), 400


@bp.route("/dashboard/communicate/download/<int:attachment_id>", methods=["GET"])
def download_attachment(attachment_id):
    """Download an attachment by its ID."""
    attachment = Attachment.query.get(attachment_id)
    if not attachment:
        return jsonify({"error": "Attachment not found"}), 404

    return send_from_directory(
        directory=app.config["UPLOAD_FOLDER"],
        path=attachment.filename,
        as_attachment=True,
        attachment_filename=attachment.filename,
    )


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


@bp.route("/dashboard/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
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
