#!/usr/bin/python
#
# 2010 Ryan Martin

# import os

from .User import User
from .Gmail import Gmail


class EnsomniacMail:
    def __init__(self, sender_email):
        self.user = User(sender_email)
        self.gmail = Gmail(sender_email)
        self.sender = self.verify_sender(sender_email)
        self.user_data = self.user.data
        self.sender_name = ""
        self.subject = ""
        self.body_html = ""
        self.body_text = ""
        self.body = ""
        self.recipients = []
        self.bcc_recipients = []
        self.reply_to = ""

    def verify_sender(self, sender_email):
        # The first step is to make sure that the send-from
        # e-mail is actually authenticated through our system
        # Check the user data to find the user token and verify
        # the token is still good. If it's good, no need to do anything.
        # If there is a problem, raise an exception.

        http_auth = self.gmail.get_http_auth(self.user.data)

        if not bool(http_auth):
            raise Exception("The send-from e-mail address '" + sender_email + "' is not authenticated through our mail system. To authenticate, do these steps...")

        return sender_email

    def set_reply_to(self, email, name=""):
        self.reply_to = self.generate_recipient_str(email, name)

    def set_sender_name(self, name):
        # Sets the display name for the e-mail. First name and last name is used as a default.
        self.sender_name = name

    def set_subject(self, subject):
        # The subject of the e-mail
        self.subject = subject

    def set_body_html(self, html):
        # The body of the e-mail, with HTML tags allowed
        self.body_html = html

    def set_body_text(self, text):
        # An optional text only variation of the e-mail, in case a
        # recipient can't get HTML e-mails for some weird reason
        self.body_text = text

    def set_body(self, body):
        self.body_text = body
        self.body_html = body

    def add_recipient(self, email, name=""):
        # Add a recipient
        # If we pass a name, the message is composed with the proper bracket name string:
        self.recipients.append(self.generate_recipient_str(email, name))

    def add_bcc_recipient(self, email, name=""):
        # Add a bcc recipient
        # If we pass a name, the message is composed with the proper bracket name string:
        self.bcc_recipients.append(self.generate_recipient_str(email, name))

    # TODO: This can likely be replaced by email.utils.formataddr
    def generate_recipient_str(self, email, name=""):
        # Convert <email> & <First name, Last Name> into "Ryan Martin <ryan@ensomniac.com>"
        if name:
            # "Ryan Martin <ryan@ensomniac.com>"
            recipient_str = name + " <" + email + ">"
        else:
            recipient_str = email

        return recipient_str

    def send(self, email=None, name=""):
        # Check to make sure we have all the parts we need
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

        if email:
            batch_addition = self.generate_recipient_str(email, name)

            local_recipients.append(batch_addition)

        send_error = self.gmail.send_message(
            self.user_data,
            self.body_text,
            self.body_html,
            local_recipients,
            self.subject,
            self.bcc_recipients,
            self.sender_name,
            self.reply_to
        )

        return {
            "error": None,
            "send_error": send_error
        }


# This lets us import the module and call Mail.create("ryan@ensomniac.com")
# It will return an instance of the EnsomniacMail class
def create(sender_email):
    return EnsomniacMail(sender_email)
