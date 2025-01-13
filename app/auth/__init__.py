#!/usr/bin/env python3
"""Initialization Module"""
from flask import Blueprint

bp = Blueprint("auth", __name__)

from app.auth import routes
