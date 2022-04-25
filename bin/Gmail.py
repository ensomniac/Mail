#!/usr/bin/python
#
# 2010 Ryan Martin

# import os
# import datetime
import os.path

from .User import User
from email.mime.text import MIMEText
from logging import basicConfig, CRITICAL
from email.mime.multipart import MIMEMultipart

basicConfig(level=CRITICAL)


class Gmail:
    def __init__(self, user):
        self.user = User(user)

    def send_message(self, user_data, body_text, body_html, recipients, subject, bcc_recipients=[], sender_name="", reply_to="", attachment_file_paths=[]):
        from base64 import urlsafe_b64encode

        http_auth = self.get_http_auth(user_data)
        service = self.get_service(http_auth)

        # Creating message
        message = MIMEMultipart("alternative")
        message["to"] = ",".join(recipients)

        if bcc_recipients:
            message["bcc"] = ",".join(bcc_recipients)

        tag = "<" + self.user.email + ">"

        if sender_name:
            if tag not in sender_name:
                sender_name += tag

            message["from"] = sender_name
        else:
            message["from"] = self.user.first_name + " " + self.user.last_name + tag

        if reply_to:
            message["Reply-To"] = reply_to

        message["subject"] = subject

        message.attach(MIMEText(body_text, "plain"))
        message.attach(MIMEText(body_html, "html"))

        if attachment_file_paths:
            for file_path in attachment_file_paths:
                message = self.add_attachment_to_message(message, file_path)

        # message_raw = dict(raw=urlsafe_b64encode(message.as_string().encode()).decode())
        # message_raw = urlsafe_b64encode(message.as_string().encode())
        message_raw = message.as_string()

        service.users().messages().send(userId="me", body=message_raw).execute()

    def add_attachment_to_message(self, message, file_path):
        if not os.path.exists(file_path):
            return message

        from os.path import basename
        from mimetypes import guess_type

        content_type, encoding = guess_type(file_path)

        if content_type is None or encoding is not None:
            content_type = "application/octet-stream"

        main_type, sub_type = content_type.split("/", 1)
        file_reader = open(file_path, "rb")
        file_bytes = file_reader.read()

        if main_type == "text":
            attachment = MIMEText(file_bytes, _subtype=sub_type)

        elif main_type == "image":
            from email.mime.image import MIMEImage

            attachment = MIMEImage(file_bytes, _subtype=sub_type)

        elif main_type == "audio":
            from email.mime.audio import MIMEAudio

            attachment = MIMEAudio(file_bytes, _subtype=sub_type)

        else:
            from email.mime.base import MIMEBase

            attachment = MIMEBase(main_type, sub_type)

            attachment.set_payload(file_bytes)

        file_reader.close()

        attachment.add_header("Content-Disposition", "attachment", filename=basename(file_path))

        message.attach(attachment)

        return message

    def get_http_auth(self, user_data):
        from httplib2 import Http
        from oauth2client import client

        access_token_credentials = client.AccessTokenCredentials(user_data["access_token"], "my-user-agent/1.0")  # <oauth2client.client.AccessTokenCredentials object at 0x10fb63c10>
        oauth2_credentials_object = access_token_credentials.new_from_json(user_data["credentials_to_json"])  # <oauth2client.client.OAuth2Credentials object at 0x10fb633d0>

        if oauth2_credentials_object.access_token_expired:
            # Access token has expired and a refresh is required

            oauth2_credentials_object.refresh(Http())

            http_auth = oauth2_credentials_object.authorize(Http())
        else:
            http_auth = oauth2_credentials_object.authorize(Http())

        return http_auth

    # Building service....
    def get_service(self, http_auth):
        from apiclient import discovery

        return discovery.build("gmail", "v1", http_auth)  # <googleapiclient.discovery.Resource object at 0x2a16510>
