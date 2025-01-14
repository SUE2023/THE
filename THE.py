#!/usr/bin/env python3
"""Main Application Module"""
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import User
from app import cli
from utils.file_utils import allowed_file

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"sa": sa, "so": so, "db": db, "User": User}


if __name__ == "__main__":
    app.run(debug=True)
