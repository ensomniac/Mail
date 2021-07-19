#!/usr/bin/python2
# -*- coding: ascii -*-
#
# 2010 Ryan Martin

import os

from . import User
from . import Gmail

class EnsomniacMail:
    def __init__(self, sender_email):
        self.sender = self.verify_sender(sender_email)
        self.gmail = Gmail.Gmail(self.sender)
        self.user = User.User(self.sender)
        self.user_data = self.user.get_user_data()

        self.sender_name = ""
        self.subject = ""
        self.body_html = ""
        self.body_text = ""
        self.body = ""
        self.recipients = []
        self.bcc_recipients = []

    def verify_sender(self, sender_email):
        # The first step is to make sure that the send from
        # e-mail is actually authenticated through our system
        # Check the user data to find the user token and verify
        # the token is still good. If it's good, no need to do anything.
        # If there is a problem, raise an exception.

        user = User.User(sender_email)

        http_auth = Gmail.Gmail(sender_email).get_http_auth(user.get_user_data())

        if http_auth:
            sender_valid = True

        if not sender_valid:
            raise Exception("The send-from e-mail address '" + self.sender + "' is not authenticated through our mail system. To authenticate, do these steps...")

        return sender_email

    def set_sender_name(self, sender_name):
        # Sets the display name for the e-mail. First name and last name is used as a default.
        self.sender_name = sender_name

    def set_subject(self, subject):
        # The subject of the e-mail
        self.subject = subject

    def set_body_html(self, body_html):
        # The body of the e-mail, with HTML tags allowed
        self.body_html = body_html

    def set_body_text(self, body_text):
        # An optional text only variation of the e-mail, in case a
        # recipient can't get HTML e-mails for some weird reason
        self.body_text = body_text

    def set_body(self, body):

        self.body_text = body
        self.body_html = body

    def add_recipient(self, recipient_email, recipient_name=""):
        # Add a recipient
        # If we pass a name, the message is composed with the proper bracket name string:

        self.recipients.append(self.generate_recipient_str(recipient_email, recipient_name))

    def add_bcc_recipient(self, bcc_recipient_email, bcc_recipient_name=""):
        # Add a bcc recipient
        # If we pass a name, the message is composed with the proper bracket name string:

        self.bcc_recipients.append(self.generate_recipient_str(bcc_recipient_email, bcc_recipient_name))

    def generate_recipient_str(self, recipient_email, recipient_name=""):
        # Convert <email> & <First name, Last Name> into "Ryan Martin <ryan@ensomniac.com>"

        if recipient_name:
            # "Ryan Martin <ryan@ensomniac.com>"
            recipient_str = recipient_name + " <" + recipient_email + ">"
        else:
            recipient_str = recipient_email

        return recipient_str


    def send(self, recipient_email=None, recipient_name=""):
        # Check to make sure we have all of the parts we need
        # Use the gmail API to send the mail

        # recipient_email = used for batch sending
        # recipient_name = used for batch sending

        if not self.body_text:
            self.body_text = self.body_html

        if not self.body_html:
            self.body_html = self.body_text

        if not self.subject:
            return {"error": "subject not specified"}

        local_recipients = []
        for recipient in self.recipients:
            local_recipients.append(recipient)

        if recipient_email:
            batch_addition = self.generate_recipient_str(recipient_email, recipient_name)
            local_recipients.append(batch_addition)

        send_error = self.gmail.send_message(
            self.user_data,
            self.body_text,
            self.body_html,
            local_recipients,
            self.subject,
            self.bcc_recipients,
            self.sender_name
        )

        send_result = {"error": None, "send_error": send_error}

        return send_result

# This lets us import the module and call Mail.create("ryan@ensomniac.com")
# It will return an instance of the EnsomniacMail class
def create(sender_email):
    return EnsomniacMail(sender_email)

