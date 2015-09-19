from flask import Flask
# import twilio.twiml

app = Flask(__name__)

import logging
file_handler = logging.FileHandler("log.txt")
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)
 
 
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()
    resp.say("Hello Monkey")
 
    return str(resp)
 