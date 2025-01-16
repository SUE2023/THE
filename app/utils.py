#!/usr/bin/env python3
""" Utility Module"""
import os
from flask import current_app

def allowed_file(filename):
    """
    Check if the file extension is allowed based on the application's configuration.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    # Get allowed extensions from the app's config
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']

    # Extract the file extension (case insensitive)
    file_ext = os.path.splitext(filename)[1].lower()

    # Check if the file extension is in the allowed list
    return file_ext in allowed_extensions
