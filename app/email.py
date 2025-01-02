#!/usr/bin/env python3
"""Email Module"""

from flask_mail import Message
from app import mail

def send_email(subject, sender, recipients, cc=None, bcc=None, text_body=None, html_body=None):
    """
    Sends an email using Flask-Mail.

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
    mail.send(msg)
