#!/usr/bin/env python3
"""Initilization Module"""
from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers
