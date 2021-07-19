#!/usr/bin/python2
#
# Author:  Ryan Martin ryan@ensomniac.com
#

import os
import cgi
import httplib2

import User

class Authorize:
    def __init__(self):

        self.gmail_client_id = "947806183438-e1hirfb16k1h1d4jnc7u05u1vu3n2pnh.apps.googleusercontent.com"
        self.gmail_client_secret = "EjgANOKgqRT2FViDD7nyjj58"
        self.scope = ["https://mail.google.com/", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
        self.redirect_uri = "https://mail.oapi.co/code" # code=sdiofjdsfoidjs

        self.redirect_url = None


    def get_flow(self):
        from oauth2client import client
        from oauth2client.client import OAuth2WebServerFlow

        flow = OAuth2WebServerFlow(
            client_id=self.gmail_client_id,
            client_secret=self.gmail_client_secret,
            scope=self.scope,
            redirect_uri=self.redirect_uri
        )

        flow.params['access_type'] = 'offline'         # offline access
        flow.params['include_granted_scopes'] = "true"   # incremental auth

        return flow


    def get_auth_url(self):
    # Step 1
    # Get googles URL, provide a way to click URL
        flow = self.get_flow()
        self.redirect_url = flow.step1_get_authorize_url()

        return self.redirect_url


    def exchange_code(self, code):

        # Step 2: Exchange an authorization code for OAuth2 Credentials
        flow = self.get_flow()
        credentials = flow.step2_exchange(code)

        # If no refresh token is provided it means user has already been authorized.
        if not credentials.refresh_token:
            # In order to store refresh token we need to revoke current credentials.
            credentials.revoke(httplib2.Http())
            # Send user back through authorization flow
            self.get_auth_url()
            self.return_data = {"error": "No refresh token"}

            raise Exception("Failed to exchange code: " + str(code))

            return

        return credentials


    # def build_user_data(self):
    #     # Obtain email_address then store credentials in filename: email_address

    #     from apiclient import discovery

    #     credentials = self.exchange_code()
    #     http_auth = credentials.authorize(httplib2.Http())
    #     service = discovery.build("gmail", "v1", http_auth)

    #     profile = service.users().getProfile(userId="me").execute() # "profile": "{u'threadsTotal': 3127, u'emailAddress': u'katie.hilder@gmail.com', u'historyId': u'2049990', u'messagesTotal': 5632}", "error": null}
    #     email_address = profile.get("emailAddress")

    #     # If no refresh token is provided it means user has already been authorized.
    #     if not credentials.refresh_token:
    #         # In order to store refresh token we need to revoke current credentials.
    #         credentials.revoke(httplib2.Http())
    #         # Send user back through authorization flow
    #         self.authorize()
    #         self.return_data = {"error": "No refresh token"}
    #         return

    #     self.return_data = {"error": None, "user_data": user_data}
    #     return self.return_data


# Outside of class

def get_auth_url():
    auth_url = Authorize().get_auth_url()
    return auth_url

def exchange_code(code):
    credentials = Authorize().exchange_code(code)
    return credentials

# user = User.User("katie.hilder@gmail.com")
# print user.get_user_data()
