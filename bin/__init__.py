#!/usr/bin/python
#
# Ensomniac 2025 Ryan Martin, ryan@ensomniac.com
#                Andrew Stet, stetandrew@gmail.com

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
        self.attachment_file_paths = []

    def verify_sender(self, sender_email):
        # The first step is to make sure that the send-from
        # email is actually authenticated through our system
        # Check the user data to find the user token and verify
        # the token is still good. If it's good, no need to do anything.
        # If there is a problem, raise an exception.

        http_auth = self.gmail.get_http_auth(self.user.data)

        if not bool(http_auth):
            raise Exception(
                f"The send-from email address '{sender_email}' is not authenticated through "
                f"our mail system.\n\nTo authenticate, visit:\nhttps://authorize.oapi.co/gmail"
            )

        return sender_email

    def add_attachment(self, file_path):
        if file_path not in self.attachment_file_paths:
            self.attachment_file_paths.append(file_path)

    def set_reply_to(self, email, name=""):
        self.reply_to = self.generate_recipient_str(email, name)

    def set_sender_name(self, name):
        # Sets the display name for the email. First name and last name is used as a default.
        self.sender_name = name

    def set_subject(self, subject):
        # The subject of the email
        self.subject = subject

    def set_body_html(self, html):
        # The body of the email, with HTML tags allowed
        self.body_html = html

    def set_body_text(self, text):
        # An optional text only variation of the email, in case a
        # recipient can't get HTML emails for some weird reason
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
            user_data=self.user_data,
            body_text=self.body_text,
            body_html=self.body_html,
            recipients=local_recipients,
            subject=self.subject,
            bcc_recipients=self.bcc_recipients,
            sender_name=self.sender_name,
            reply_to=self.reply_to,
            attachment_file_paths=self.attachment_file_paths
        )

        return {
            "error": None,
            "send_error": send_error
        }


# This lets us import the module and call Mail.create("ryan@ensomniac.com")
# It will return an instance of the EnsomniacMail class
def create(sender_email):
    return EnsomniacMail(sender_email)
