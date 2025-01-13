#!/usr/bin/env python3
"""Email Module"""
from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(
    subject, sender, recipients, cc=None, bcc=None, text_body=None, html_body=None
):
    """
    Sends an email using Flask-Mail, either synchronously or asynchronously.

    Parameters:
        - subject (str): Subject of the email.
        - sender (str): Sender's email address.
        - recipients (list): List of recipient email addresses.
        - cc (list, optional): List of CC email addresses.
        - bcc (list, optional): List of BCC email addresses.
        - text_body (str, optional): Plain text content of the email.
        - html_body (str, optional): HTML content of the email.
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    if cc:
        msg.cc = cc
    if bcc:
        msg.bcc = bcc
    if text_body:
        msg.body = text_body
    if html_body:
        msg.html = html_body
    # Process attachments
    if attachments:
        for attachment in attachments:
            if len(attachment) == 3:  # Ensure correct format
                msg.attach(*attachment)
            else:
                raise ValueError(
                    "Each attachment must be a tuple (filename, content, type)"
                )

    # Send email
    if sync:
        mail.send(msg)
    else:
        Thread(
            target=send_async_email, args=(current_app._get_current_object(), msg)
        ).start()


def send_async_email(app, msg):
    """
    Sends an email asynchronously.
    """
    with app.app_context():
        mail.send(msg)
