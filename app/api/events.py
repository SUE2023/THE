#!/usr/bin/env python3
"""Event Module"""
from flask import jsonify, request, url_for
from flask_login import current_user, login_required
from app import db
from app.models import CalendarEvent
from app.api import bp
from app.api.errors import bad_request

@bp.route('/calendar/events', methods=['GET'])
@login_required
def get_events():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = current_user.calendar_events.order_by(CalendarEvent.start_time)
    data = CalendarEvent.to_collection_dict(query, page, per_page, 'api.get_events')
    return jsonify(data)

@bp.route('/calendar/events', methods=['POST'])
@login_required
def create_event():
    data = request.get_json() or {}
    if 'title' not in data or 'start_time' not in data or 'end_time' not in data:
        return bad_request('Missing required fields')
    event = CalendarEvent(user=current_user)
    event.from_dict(data, include_fields=['title', 'start_time', 'end_time', 'description'])
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201

@bp.route('/calendar/events/<int:id>', methods=['PUT'])
@login_required
def update_event(id):
    event = current_user.calendar_events.filter_by(id=id).first_or_404()
    data = request.get_json() or {}
    event.from_dict(data, include_fields=['title', 'start_time', 'end_time', 'description'])
    db.session.commit()
    return jsonify(event.to_dict())

@bp.route('/calendar/events/<int:id>', methods=['DELETE'])
@login_required
def delete_event(id):
    event = current_user.calendar_events.filter_by(id=id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    return '', 204

