#!/usr/bin/python
#
# 2010 Ryan Martin

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
        self.redirect_uri = "https://mail.socat.co/code" # code=sdiofjdsfoidjs

        # self.redirect_url = None

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

            try:
                credentials.revoke(httplib2.Http())
            except:
                raise Exception("Failed to revoke, but did we need to revoke?")


            # Send user back through authorization flow
            self.get_auth_url()
            self.return_data = {"error": "No refresh token"}

            raise Exception("Failed to exchange code: " + str(code))

            return

        return credentials

def get_auth_url():
    auth_url = Authorize().get_auth_url()
    return auth_url

def exchange_code(code):
    credentials = Authorize().exchange_code(code)
    return credentials

# user = User.User("katie@gmail.com")
# print user.get_user_data()
