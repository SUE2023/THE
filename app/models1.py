#!/usr/bin/env python3
""" User database model"""
from datetime import datetime, timezone, timedelta
from hashlib import md5
from flask import current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_login import UserMixin
import json
import secrets
from time import time
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from typing import Optional, List, Dict
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, page=page, per_page=per_page, error_out=False)
        data = {
            "items": [item.to_dict() for item in resources.items],
            "_meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": resources.pages,
                "total_items": resources.total,
            },
            "_links": {
                "self": url_for(endpoint, page=page, per_page=per_page, **kwargs),
                "next": (
                    url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                    if resources.has_next
                    else None
                ),
                "prev": (
                    url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                    if resources.has_prev
                    else None
                ),
            },
        }
        return data


class CalendarEvent(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    title: so.Mapped[str] = so.mapped_column(sa.String(128), nullable=False)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    start_time: so.Mapped[datetime] = so.mapped_column(nullable=False)
    end_time: so.Mapped[datetime] = so.mapped_column(nullable=False)
    is_recurring: so.Mapped[bool] = so.mapped_column(default=False)
    recurrence_pattern: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(64)
    )  # E.g., 'daily', 'weekly', etc.
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Convert CalendarEvent instance to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "is_recurring": self.is_recurring,
            "recurrence_pattern": self.recurrence_pattern,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def from_dict(self, data, include_fields=None):
        """Update instance attributes from a dictionary with field restrictions."""
        include_fields = include_fields or []
        allowed_fields = {
            "title",
            "description",
            "start_time",
            "end_time",
            "is_recurring",
            "recurrence_pattern",
        }
        fields_to_update = allowed_fields.intersection(include_fields)
        for field in fields_to_update:
            if field in data:
                setattr(self, field, data[field])


class Resource(Base):
    """Model for resources stored in SQLite."""

    __tablename__ = "resources"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    image_id = Column(String(24), nullable=True)  # Store MongoDB image ID here


class Contact(db.Model):
    """Model representing organizational contacts."""

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), nullable=False)
    phone_number: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(15), nullable=True
    )
    email: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128), nullable=True)
    organization: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(128), nullable=True
    )

    def to_dict(self) -> Dict:
        """Convert Contact instance to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "organization": self.organization,
        }

    def from_dict(self, data: Dict, include_fields: Optional[List[str]] = None):
        """Update instance attributes from a dictionary."""
        include_fields = include_fields or []
        allowed_fields = {"name", "phone_number", "email", "organization"}
        fields_to_update = allowed_fields.intersection(include_fields)
        for field in fields_to_update:
            if field in data:
                setattr(self, field, data[field])


class Communication(db.Model):
    """Model representing user communication logs."""

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    sent_message: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(140), nullable=True
    )
    received_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self) -> Dict:
        """Convert Communication instance to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "sent_message": self.sent_message,
            "received_at": self.received_at.isoformat(),
        }

    def from_dict(self, data: Dict, include_fields: Optional[List[str]] = None):
        """Update instance attributes from a dictionary."""
        include_fields = include_fields or []
        allowed_fields = {"username", "sent_message"}
        fields_to_update = allowed_fields.intersection(include_fields)
        for field in fields_to_update:
            if field in data:
                setattr(self, field, data[field])

     # Relationships
    contact: Mapped['Contact'] = relationship('Contact', back_populates='communications')
    attachments: Mapped[list['Attachment']] = relationship('Attachment', back_populates='communication')


class Attachment(db.Model):
    __tablename__ = "attachment"

    id: Mapped[int] = mapped_column(primary_key=True)
    communication_id: Mapped[int] = mapped_column(
        ForeignKey("communication.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filetype: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., 'image/jpeg', 'application/pdf'
    filepath: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # File storage path

    # Relationship
    communication: Mapped["Communication"] = relationship(
        "Communication", back_populates="attachments"
    )

    # Relationship
    communication: Mapped['Communication'] = relationship('Communication', back_populates='attachments')


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    last_message_read_time: so.Mapped[Optional[datetime]]
    token: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(32), index=True, unique=True
    )
    token_expiration: so.Mapped[Optional[datetime]]
    calendar_events: so.WriteOnlyMapped[List["CalendarEvent"]] = so.relationship(
        "CalendarEvent", backref="user", lazy="dynamic"
    )

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except Exception:
            return
        return db.session.get(User, id)

    def to_dict(self, include_email=False):
        data = {
            "id": self.id,
            "username": self.username,
            "last_seen": (
                self.last_seen.replace(tzinfo=timezone.utc).isoformat()
                if self.last_seen
                else None
            ),
            "about_me": self.about_me,
            "_links": {
                "self": url_for("api.get_user", id=self.id),
                "avatar": self.avatar(128),
            },
        }
        if include_email:
            data["email"] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ["username", "email", "about_me"]:
            if field in data:
                setattr(self, field, data[field])
        if new_user and "password" in data:
            self.set_password(data["password"])

    def get_token(self, expires_in=3600):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(
            tzinfo=timezone.utc
        ) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now(timezone.utc) - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration.replace(
            tzinfo=timezone.utc
        ) < datetime.now(timezone.utc):
            return None
        return user


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
