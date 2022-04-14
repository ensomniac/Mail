#!/usr/bin/python
#
# 2010 Ryan Martin

# TODO: Is this now deprecated in favor of the Dash.Authenticate module?

import os
import sys


class Authorize:
    def __init__(self):

        self.gmail_client_id, self.gmail_client_secret, self.redirect_uri = self.get_google_client()

        self.scope = [
            "https://mail.google.com/",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]

    def get_google_client(self):
        config_path = "/etc/mail.d/google_client_config"

        if not os.path.exists(config_path):
            print("\nERROR: Missing Google Config! Expected " + config_path + "\n")
            sys.exit()

        gmail_client_id = None
        gmail_client_secret = None
        redirect_uri = None

        for line in open(config_path, "r").read().split("\n"):
            line = line.strip()
            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            if line.startswith("gmail_client_id"):
                gmail_client_id = line.split("=")[-1].strip()

            if line.startswith("gmail_client_secret"):
                gmail_client_secret = line.split("=")[-1].strip()

            if line.startswith("redirect_uri"):
                redirect_uri = line.split("=")[-1].strip()

        print("gmail_client_id: " + str(gmail_client_id))
        print("gmail_client_secret: " + str(gmail_client_secret))
        print("redirect_uri: " + str(redirect_uri))

        return gmail_client_id, gmail_client_secret, redirect_uri

    def get_flow(self):
        # from oauth2client import client
        from oauth2client.client import OAuth2WebServerFlow

        flow = OAuth2WebServerFlow(
            client_id=self.gmail_client_id,
            client_secret=self.gmail_client_secret,
            scope=self.scope,
            redirect_uri=self.redirect_uri
        )

        flow.params['access_type'] = 'offline'  # offline access
        flow.params['include_granted_scopes'] = "true"  # incremental auth
        flow.params['prompt'] = "consent"  # https://github.com/googleapis/google-api-python-client/issues/213

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

        try:
            credentials = flow.step2_exchange(code)
        except:
            from traceback import format_exc

            err = format_exc()
            self.return_data = {"error": "Failed step2_exchange w/ code: " + str(code) + " TB >> " + err}
            return

        # raise Exception("REFRESH TOKEN: " + str(credentials.refresh_token))
        # raise Exception(credentials)

        # If no refresh token is provided it means user has already been authorized.
        if not credentials.refresh_token:
            # In order to store refresh token we need to revoke current credentials.

            try:
                from httplib2 import Http
                credentials.revoke(Http())
            except:
                from traceback import format_exc

                raise Exception("Failed to revoke, but did we need to revoke? ERROR: " + str(format_exc()))
                # pass

            # Send user back through authorization flow
            self.get_auth_url()
            self.return_data = {"error": "No refresh token"}

            from traceback import format_exc

            raise Exception("Failed to exchange code: " + str(code) + " ERR: " + format_exc())

            # return

        return credentials


def get_auth_url():
    auth_url = Authorize().get_auth_url()
    return auth_url


def exchange_code(code):
    credentials = Authorize().exchange_code(code)
    return credentials
