#!/usr/bin/env python3
"""Utility functions related to file handling """
def allowed_file(filename, allowed_extensions):
    """
    Check if the file extension is allowed.
    :param filename: Name of the uploaded file
    :param allowed_extensions: Set of allowed file extensions
    :return: True if the file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
