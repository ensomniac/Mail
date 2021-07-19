#!/usr/bin/python2

import os

# os.chdir("/var/www/vhosts/oapi.co/mail/cgi-bin/")
# current_path = os.getcwd()


from . import User
from . import Gmail

# Usage, from anywhere on oapi:
#
# import Mail
# message = Mail.create("ryan@ensomniac.com")
# message.add_recipient("katie@gmail.com")
# message.set_subject("Hello!")
# message.set_body_html("What is up!?")
# result = message.send()

class EnsomniacMail:
    def __init__(self, sender_email):
        self.sender = self.verify_sender(sender_email)
        self.gmail = Gmail.Gmail(self.sender)
        self.user = User.User(self.sender)
        self.user_data = self.user.get_user_data()

        self.sender_name = ""
        self.subject = ""
        self.body_html = ""
        self.body_text = ""
        self.body = ""
        self.recipients = []
        self.bcc_recipients = []

    def verify_sender(self, sender_email):
        # The first step is to make sure that the send from
        # e-mail is actually authenticated through our system
        # Check the user data to find the user token and verify
        # the token is still good. If it's good, no need to do anything.
        # If there is a problem, raise an exception.

        user = User.User(sender_email)

        http_auth = Gmail.Gmail(sender_email).get_http_auth(user.get_user_data())

        if http_auth:
            sender_valid = True

        if not sender_valid:
            raise Exception("The send-from e-mail address '" + self.sender + "' is not authenticated through our mail system. To authenticate, do these steps...")

        return sender_email

    def set_sender_name(self, sender_name):
        # Sets the display name for the e-mail. First name and last name is used as a default.
        self.sender_name = sender_name

    def set_subject(self, subject):
        # The subject of the e-mail
        self.subject = subject

    def set_body_html(self, body_html):
        # The body of the e-mail, with HTML tags allowed
        self.body_html = body_html

    def set_body_text(self, body_text):
        # An optional text only variation of the e-mail, in case a
        # recipient can't get HTML e-mails for some weird reason
        self.body_text = body_text

    def set_body(self, body):

        self.body_text = body
        self.body_html = body

    def add_recipient(self, recipient_email, recipient_name=""):
        # Add a recipient
        # If we pass a name, the message is composed with the proper bracket name string:

        self.recipients.append(self.generate_recipient_str(recipient_email, recipient_name))

    def add_bcc_recipient(self, bcc_recipient_email, bcc_recipient_name=""):
        # Add a bcc recipient
        # If we pass a name, the message is composed with the proper bracket name string:

        self.bcc_recipients.append(self.generate_recipient_str(bcc_recipient_email, bcc_recipient_name))

    def generate_recipient_str(self, recipient_email, recipient_name=""):
        # Convert <email> & <First name, Last Name> into "Ryan Martin <ryan@ensomniac.com>"

        if recipient_name:
            # "Ryan Martin <ryan@ensomniac.com>"
            recipient_str = recipient_name + " <" + recipient_email + ">"
        else:
            recipient_str = recipient_email

        return recipient_str


    def send(self, recipient_email=None, recipient_name=""):
        # Check to make sure we have all of the parts we need
        # Use the gmail API to send the mail

        # recipient_email = used for batch sending
        # recipient_name = used for batch sending

        if not self.body_text:
            self.body_text = self.body_html

        if not self.body_html:
            self.body_html = self.body_text

        # if not self.recipients:
        #     return {"error": "recipients not specified"}

        if not self.subject:
            return {"error": "subject not specified"}

        local_recipients = []
        for recipient in self.recipients:
            local_recipients.append(recipient)

        if recipient_email:
            batch_addition = self.generate_recipient_str(recipient_email, recipient_name)
            local_recipients.append(batch_addition)

        send_error = self.gmail.send_message(
            self.user_data,
            self.body_text,
            self.body_html,
            local_recipients,
            self.subject,
            self.bcc_recipients,
            self.sender_name
        )

        send_result = {"error": None, "send_error": send_error}

        return send_result


# This lets us import the module and call Mail.create("ryan@ensomniac.com")
# It will return an instance of the EnsomniacMail class
def create(sender_email):
    return EnsomniacMail(sender_email)



# def get_html_for_reminder(email_address, street_name, street_suffix, pick_up_type, pick_up_day):

#     header = "Ringwood, NJ: " + pick_up_type.title() + " Collection Reminder"
#     core_message = "Hi " + email_address + ",<br><br>"
#     core_message += pick_up_type.title() + " for <b>" + street_name.title() + " " + street_suffix.title() + "</b> will be collected " + pick_up_day + "."
#     core_message += " Don't forget to take your " + pick_up_type + " out! <br><br>"
#     core_message += "Have a nice day!"

#     disclaimer = "You have received this email because you have subscribed at ringwood.oapi.co to recieve an email reminder. <br>"
#     disclaimer += "You can always unsubscribe from our mailing list, by clicking on "
#     disclaimer += "<a href=""http://ringwood.oapi.co/cgi-bin/api.py?f=unsubscribe&email=" + email_address + ">Unsubscribe</a>"

#     header_styles = {
#         "background": "rgba(56, 86, 44, 1.0)",
#         "font-size": "18px",
#         "color": "rgba(255, 255, 255, 0.8)",
#         "padding": "20px",
#     }

#     body_styles = {
#         "background": "rgba(0, 0, 0, 0.2)",
#         "font-size": "15px",
#         "padding-top": "40px",
#         "padding-left": "20px",
#         "padding-bottom": "40px",
#         }

#     unsubscribe_text_styles = {
#         "background": "rgba(56, 86, 44, 1.0)",
#         "font-size": "12px",
#         "color": "rgba(255, 255, 255, 0.7)",
#         "text-align": "center",
#         "padding": "10px",
#     }

#     header_style = ""
#     for key in header_styles:
#         header_style += key + ":" + header_styles[key] + ";"


#     body_style = ""
#     for key in body_styles:
#         body_style += key + ":" + body_styles[key] + ";"

#     unsubscribe_text_style = ""
#     for key in unsubscribe_text_styles:
#         unsubscribe_text_style += key + ":" + unsubscribe_text_styles[key] + ";"

#     msg = []
#     msg.append("<div class='reminder_container'>")
#     msg.append("<div style='" + header_style + "'>" + header + "</div>")
#     msg.append("<div style='" + body_style + "'>" + core_message + "</div>")
#     msg.append("<div style='" + unsubscribe_text_style + "'>" + disclaimer + "</div>")
#     msg.append("</div>")

#     final_msg = "\n".join(msg)

#     return final_msg



# For kate to test:
# Confirm that it still works the way it did
#
# Also, confirm that batch sending works and is as fast as possible:

# message = create("admin@ensomniac.com")
# message.set_sender_name("Rock On")
# message.add_recipient("katie.hilder@gmail.com")
# message.set_subject("Hello - this is batch test!")

# batch = []
# batch_names = {}
# batch_names["katieandkarihilder@gmail.com"] = {"pickup_type": "recycling", "user_data": {"email_address": "katieandkarihilder@gmail.com", "street_id": "102116242326301823"}}
# batch_names["katie.hilder@gmail.com"] = {"pickup_type": "recycling", "user_data": {"email_address": "katie.hilder@gmail.com", "street_id": "2210161414"}}
# batch_names["katiehilder@hotmail.com"] = {"pickup_type": "recycling", "user_data": {"email_address": "katiehilder@hotmail.com", "street_id": "2818243033"}}
# batch.append(batch_names)
# # print batch

# for batch_dict in batch:
#     # print batch_dict
#     for user in batch_dict:
#         user_dict = batch_dict[user]
#         user_data = user_dict["user_data"]
#         print user_data

    # street_name = batch_names[email]["street_name"]
    # street_suffix = batch_names[email]["suffix"]

    # message.set_body_html(get_html_for_reminder(email, street_name, street_suffix, "recycling", "today"))

    # result = message.send(email)

# message = Mail.create(self.senders_email)
# message.set_sender_name(self.senders_name)
# message.add_recipient("Katie Hilder <katie.hilder@gmail.com>")
# message.add_recipient("Ryan Martin <ryan@ensomniac.com>")
# message.set_subject(subject)
# message.set_body_html(body)
#
# for email in batch_names:
#    full_name = batch_names[email]
#    msg.send(email, full_name)



# Sending Test Email
# message = create("admin@ensomniac.com")
# message.add_recipient("katie.hilder@gmail.com")
# message.set_sender_name("Rock On")
# # # message.add_bcc_recipient("Katie Hilder <katiehilder@hotmail.com>")
# message.set_subject("Hello - this is a test!")
# message.set_body_text("testing")
# # message.set_body_text(get_html_for_subscriber_email("katie@gmail.com", "algonquin terrace"))

# result = message.send()




