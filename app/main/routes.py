#!/usr/bin/env python3
"""Home Page Route"""
from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
