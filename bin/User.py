#!/usr/bin/python
#
# 2010 Ryan Martin

import os
import json


class User:
    def __init__(self, email=None):
        self.local_storage_path = "/var/www/vhosts/oapi.co/mail/local_storage/"

        self.email = email
        self.first_name = None
        self.last_name = None

        if self.email:
            self.data = self.get_user_data()
        else:
            self.data = {}

    def delete(self):
        expected_location = self.local_storage_path + "users/" + self.email

        if not os.path.exists(expected_location):
            return "Unable to locate authenticated user by e-mail address '" + self.email + "'"

        else:
            os.remove(expected_location)

        return "The user was removed"

    def get_user_data(self):
        expected_location = self.local_storage_path + "users/" + self.email

        if not os.path.exists(expected_location):
            user_data = self.get_user_data_new()

            if user_data:
                return user_data

            raise Exception("Unable to locate authenticated user by e-mail address '" + self.email + "' (1)")

        user_data = self.read_data(expected_location)

        if not user_data:
            raise Exception("There was a problem reading the user data for '" + self.email + "' (1)")

        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")

        return user_data

    # This is a quick and dirty hack until we properly migrate this module to Dash.
    # At that time, we'll want to update this code to only get credentials this way.
    # (Writing this with py2 syntax just in case)
    def get_user_data_new(self):
        expected_location = "/var/www/vhosts/oapi.co/authorize/local_storage/flow/" + self.email + "_gmail"

        if not os.path.exists(expected_location):
            raise Exception("Unable to locate authenticated user by e-mail address '" + self.email + "' (2)")

        full_user_data = self.read_data(expected_location)

        if not full_user_data:
            raise Exception("There was a problem reading the user data for '" + self.email + "' (2)")

        # (Temp, see note above) Convert the data to the same format that this module currently expects
        user_data = {
            "access_token": full_user_data["token_data"]["access_token"],
            "code": full_user_data["code"],
            "created_on": full_user_data["flow_initiated"],
            "credentials_to_json": json.dumps(json.dumps(full_user_data["token_data"])),  # Have stringify it twice to make it match the current escaped format
            "email": full_user_data["token_data"]["id_token"]["email"],
            "first_name": full_user_data["token_data"]["id_token"]["given_name"],
            "last_name": full_user_data["token_data"]["id_token"]["family_name"],
            "refresh_token": full_user_data["token_data"]["refresh_token"]
        }

        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")

        return user_data

    def get_token(self):
        return self.data["access_token"]

    def create(self, email, code, credentials):
        from datetime import datetime

        user_data = {
            "email": email,
            "created_on": datetime.now(),
            "code": code,
            "access_token": credentials.access_token,
            "refresh_token": credentials.refresh_token,
            "credentials_to_json": credentials.to_json(),
            "first_name": credentials.id_token.get("given_name"),
            "last_name": credentials.id_token.get("family_name")
        }

        self.data = user_data

        # Store the data on disk...
        full_path = self.local_storage_path + "users/" + email

        self.write_data(full_path, self.data)

        return self

    def add_data(self, some_dict):
        for key in some_dict:
            self.data[key] = some_dict[key]

        full_path = self.local_storage_path + "users/" + self.data["email"]
        self.write_data(full_path, self.data)

        return self

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
                        from dateutil import parser

                        datetime = parser.parse(value)
                        value = datetime
                    except:
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

    def write_data(self, full_path, data_to_write):
        data_to_write = self.datetime_to_iso(data_to_write)
        open(full_path, "w").write(json.dumps(data_to_write))

    def read_data(self, full_path):
        # data = None

        try:
            data = open(full_path, "r").read()
        except:
            raise Exception("Failed to read file: " + full_path)

        data = json.loads(data)

        data = self.iso_to_datetime(data)

        return data


def create(email, code, credentials):
    User().create(email, code, credentials)
