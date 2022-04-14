#!/usr/bin/python
#
# 2010 Ryan Martin

# import os
# import datetime
from .User import User
from email.mime.text import MIMEText
from logging import basicConfig, CRITICAL
from email.mime.multipart import MIMEMultipart

basicConfig(level=CRITICAL)


class Gmail:
    def __init__(self, user):
        self.user = User(user)

    def send_message(self, user_data, body_text, body_html, recipients, subject, bcc_recipients, sender_name=None):

        http_auth = self.get_http_auth(user_data)
        service = self.get_service(http_auth)

        # Creating message....
        message = MIMEMultipart("alternative")
        message['to'] = ",".join(recipients)
        message['bcc'] = ",".join(bcc_recipients)

        if sender_name:
            message['from'] = sender_name + "<" + self.user.email + ">"
        else:
            message['from'] = self.user.first_name + " " + self.user.last_name + "<" + self.user.email + ">"

        message['subject'] = subject

        message.attach(MIMEText(body_text, "plain"))
        message.attach(MIMEText(body_html, "html"))

        from base64 import urlsafe_b64encode

        message_raw = {'raw': urlsafe_b64encode(message.as_string().encode()).decode()}

        service.users().messages().send(userId="me", body=message_raw).execute()

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
