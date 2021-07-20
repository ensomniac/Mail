# Mail

This is old code that was used to wrap gmail. Use with care.

REQUIRES:
pip install httplib2
pip install oauth2client
pip install apiclient
pip install google-api-python-client
pip install --upgrade google-api-python-client
pip install passlib

# Example for sending mail:

import Mail
message = Mail.create("system_admin@authentic-artists.ai")
message.set_sender_name("Authentic Artists Admin <system_admin@authentic-artists.ai>")
message.add_recipient("ryan@ensomniac.com")
message.add_recipient("ryan@authentic-artists.ai")
message.set_subject("test from new server")
message.set_body_html("Test from new server")
message.send()

{'error': None, 'send_error': None}

# WSS Ports must be opened
sudo iptables -A INPUT -p tcp --dport 8335 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8334 -j ACCEPT
service iptables save

