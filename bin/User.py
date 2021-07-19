#!/usr/bin/python2
#
# 2010 Ryan Martin

import os
import datetime
import json
from dateutil import parser

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

        else: os.remove(expected_location)

        return "The user was removed"


    def get_user_data(self):

        expected_location = self.local_storage_path + "users/" + self.email

        if not os.path.exists(expected_location):
            raise Exception("Unable to locate authenticated user by e-mail address '" + self.email + "'")

        user_data = self.read_data(expected_location)

        if not user_data:
            raise Exception("There was a problem reading the user data for '" + self.email + "'")

        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")

        return user_data


    def get_token(self):
        return self.data["access_token"]


    def create(self, email, code, credentials):

        user_data = {}
        user_data["email"] = email
        user_data["created_on"] = datetime.datetime.now()
        user_data["code"] = code
        user_data["access_token"] = credentials.access_token
        user_data["refresh_token"] = credentials.refresh_token
        user_data["credentials_to_json"] = credentials.to_json()
        user_data["first_name"] = credentials.id_token.get("given_name")
        user_data["last_name"] = credentials.id_token.get("family_name")

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

def create(email, code, credentials):
    User().create(email, code, credentials)



