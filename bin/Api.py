#!/usr/bin/python
#
# 2010 Ryan Martin

import cgi
import os
import json
import traceback
import datetime

from email.mime.text import MIMEText

import base64
import requests

import Authorize
import User

class EnsomniacMailApi:
    def __init__(self, module_data):
        self.FieldStorage = cgi.FieldStorage()

        self.miniStorage = {}
        self.data = self.get_data()

        self.return_data = {"error": "Unauthorized"}

        self.html_content = None
        self.htmlTitle = None
        self.redirect_url = None

        self.local_storage_path = "/var/www/vhosts/oapi.co/mail/local_storage/"
        self.flow_path = self.local_storage_path + "flow/"

        if module_data:
            self.data = module_data
            return

        try:
            self.function = eval("self." + self.data["f"])
        except:
            self.function = None

        if self.function:
            try:
                self.function()
            except:
                tb = traceback.format_exc()
                self.return_data = {"error": "There was a scripting problem: " + str(tb)}

        if not self.html_content and not self.redirect_url and self.return_data.get("error") and len(self.return_data.keys()) == 1:
            self.html_content = self.format_error_html()

        if self.html_content:
            self.print_html()
        elif self.redirect_url:
            self._redirect()
        else:
            self.print_return_data()



    def operator(self):
        # Act as a switchboard

        service_name = self.data.get("service_name")

        if service_name == "authorize":
            self.authorize()
        elif service_name == "code":
            self.create_authorized_user()
        elif service_name == "users":
            self.display_users()
        else:
            self.return_data = {"error": "Unknown Service"}



    def authorize(self):
        # Step 1
        # Get googles URL, provide a way to click URL
        self.redirect_url = Authorize.get_auth_url()
        # self.return_data = {"error": None, "redirect_url": self.redirect_url}

    def create_authorized_user(self):

        test_path = "/var/www/vhosts/oapi.co/mail/local_storage/flow/test_flow.json"
        open(test_path, "w").write(json.dumps(self.data))

        code = self.data.get("code")

        if not code:
            self.return_data = {"error": "There was no code from Google"}
            return

        credentials = Authorize.exchange_code(code)
        email = credentials.id_token.get("email")

        new_user = User.create(email, code, credentials)

        self.html_content = self.format_success_html()
        self.return_data = self.html_content

    def display_users(self):
        expected_location = self.local_storage_path + "users/"
        all_users = os.listdir(expected_location)
        self.return_data = {"error": None, "all_users": all_users, "new_user": str(new_user)}

    def get_user_data_by_email(self, email=None):
        # This allows us to run in the browser or to be called by another internal function in this script
        if not email:
            email = self.data.get("email")

        expected_location = self.local_storage_path + "users/" + email

        file_exists = os.path.exists(expected_location)


        if not os.path.exists(expected_location):
            self.return_data = {"error": "Unable to locate authenticated user by e-mail address '" + email + "'"}
            return self.return_data

        user_data = self.read_data(expected_location)

        if not user_data:
            self.return_data = {"error": "There was a problem reading the user data for authenticated user '" + email + "'"}
            return self.return_data

        self.return_data = {"error": None, "user_data": str(user_data)}
        return self.return_data

    def format_success_html(self):
        html_content = ["You've successfully authorized your email!"]
        html_content.append("")

        style = '''style="text-decoration:none;font-weight:normal;color:#222;background:rgba(143, 133, 233, 0.2);'''
        style += '''font-size:12px;text-align:left;font-family:arial, helvetica, sans-serif;'''
        style += '''margin:10px;padding:10px;"'''

        return "<div " + style + ">" + "<br>\n".join(html_content) + "</div>"

    def format_error_html(self):
        # Print the error to the window rather than displaying it as json
        html_content = ["<b>There was a problem with this request:</b>"]
        html_content.append("")
        html_content.extend(self.return_data.get("error").split("\n"))

        style = '''style="text-decoration:none;font-weight:normal;color:#222;background:rgba(143, 133, 233, 0.2);'''
        style += '''font-size:12px;text-align:left;font-family:arial, helvetica, sans-serif;'''
        style += '''margin:10px;padding:10px;"'''

        return "<div " + style + ">" + "<br>\n".join(html_content) + "</div>"

    def datetime_to_iso(self, data_dict_or_list):

        mode_dict = False
        if "dict" in str(type(data_dict_or_list)):
            clean_data_dict_or_list = {}
            mode_dict = True
        elif "list" in str(type(data_dict_or_list)):
            clean_data_dict_or_list = []
        else:
            raise Exception("Only dicts or lists are valid for this function")

        for key in data_dict_or_list:

            if mode_dict:
                value = data_dict_or_list[key]
            else:
                value = key

            if "datetime" in str(type(value)):
                value = value.isoformat()
            elif "list" in str(type(value)):
                value = self.datetime_to_iso(value)
            elif "dict" in str(type(value)):
                value = self.datetime_to_iso(value)

            if mode_dict:
                clean_data_dict_or_list[key] = value
            else:
                clean_data_dict_or_list.append(value)

        return clean_data_dict_or_list

    def iso_to_datetime(self, data_dict_or_list):

        mode_dict = False
        if "dict" in str(type(data_dict_or_list)):
            clean_data_dict_or_list = {}
            mode_dict = True
        elif "list" in str(type(data_dict_or_list)):
            clean_data_dict_or_list = []
        else:
            raise Exception("Only dicts or lists are valid for this function")

        for key in data_dict_or_list:

            if mode_dict:
                value = data_dict_or_list[key]
            else:
                value = key

            if "str" in str(type(value)):

                if "T" in value and ":" in value and "-" in value:

                    try:
                        datetime = parser.parse(value)
                        value = datetime
                    except:
                        raise Exception("Failed to parse date " + str(value))
                        pass

            elif "list" in str(type(value)):
                value = self.iso_to_datetime(value)
            elif "dict" in str(type(value)):
                value = self.iso_to_datetime(value)

            if mode_dict:
                clean_data_dict_or_list[key] = value
            else:
                clean_data_dict_or_list.append(value)

        return clean_data_dict_or_list

    def write_data(self, fullPath, dataToWrite):
        dataToWrite = self.datetime_to_iso(dataToWrite)
        open(fullPath, "w").write(json.dumps(dataToWrite))

    def read_data(self, fullPath):
        data = None

        try:
            data = open(fullPath, "r").read()
        except:
            raise Exception("Failed to read file: " + fullPath)

        data = json.loads(data)

        data = self.iso_to_datetime(data)

        return data

    def noFunction(self):
        self.return_data = {"error": "Function not found or not specified"}

    def print_html(self):
        html_to_display = []
        html_to_display.append('Content-Type: text/html\n')

        if self.htmlTitle:
            title = self.htmlTitle
        else:
            title = "Authorization needed"

        html_to_display.append("<!DOCTYPE HTML>")
        html_to_display.append('<html lang="en-US">')
        html_to_display.append('''<head>''')
        html_to_display.append('''<meta charset="UTF-8">''')
        html_to_display.append('''<title>''' + title + '''</title>''')
        html_to_display.append('''</head>''')
        html_to_display.append('''<body style="text-decoration:none;padding:0px;margin:0px;border:0px;">''' + self.html_content + '''</body>''')
        html_to_display.append('''</html>''')

        print ("\n".join(html_to_display))

    def print_return_data(self):
        print ("Content-type: text/plain")
        print ("")
        print (str(json.dumps(self.return_data)))

    def _redirect(self):
        print ("Location:" + self.redirect_url + "\r\n")

    def get_data(self):
        data = {}

        for key in self.FieldStorage.keys():
            miniFieldStorage = self.FieldStorage[key]
            data[key] = miniFieldStorage.value

            self.miniStorage[key] = miniFieldStorage

        return data


if __name__ == "__main__":
    EnsomniacMailApi({})
