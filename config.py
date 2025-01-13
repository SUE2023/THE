#!/usr/bin/env python
"""Configuration File """
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    # General Configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB Configuration
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "mydatabase")

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["your-email@example.com"]
    LANGUAGES = ["en", "es"]

    # App configuration settings
    app.config["UPLOAD_FOLDER"] = "uploads"  # Directory for storing uploaded files
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Max upload size: 16 MB
    app.config["ALLOWED_EXTENSIONS"] = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "docx",
        "txt",
    }  # Allowed file types

    # Create the upload folder if it doesn't exist

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
