import sys, os
import logging
import random
from flask import Flask, Response, request, url_for, send_file
from flask.ext.sqlalchemy import SQLAlchemy
from tropo import Tropo

import extract

import recognize

root = logging.getLogger()
log = logging.StreamHandler(sys.stdout)
log.setLevel(logging.DEBUG)
root.addHandler(log)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    voice_query = db.Column(db.Text())

    def __repr__(self):
        return '<User id %d>' % self.userid

@app.route('/home', methods=['GET', 'POST'])
def home():
    # Generate a user cookie value.  This is kept in the url args throughout
    # the session.
    user = User()
    db.session.add(user)
    db.session.commit()
    userid = user.userid

    t = Tropo()
    t.record(
        name='myrecording',
        say='speech recognition demo',
        choices={'terminator': '#'},
        url='http://infinite-cove-6526.herokuapp.com/record?userid={0}' \
            .format(userid),
        asyncUpload=True,
        maxTime=10,
    )
    t.on(event='continue', next='./success')
    t.on(event='incomplete', next='./incomplete')
    t.on(event='error', next='./error')
    return t.RenderJson()

@app.route('/success')
def success():
    print "success"
    t = Tropo()
    t.say('Success')
    return t.RenderJson()

@app.route('/incomplete')
def incomplete():
    print "incomplete"
    t = Tropo()
    t.say('incomplete')
    return t.RenderJson()

@app.route('/error')
def error():
    print "error"
    t = Tropo()
    t.say('error')
    return t.RenderJson()

@app.route('/record', methods=['GET', 'POST'])
def record():
    print "Recording received!"

    userid = int(request.args['userid'])
    print "User: ", userid
    this_user = User.query.filter_by(userid=userid).first()

    audio = request.files['filename'].read()
    out_file = open('./test.wav', 'wb')
    out_file.write(audio)

    # Test speech recognition
    text = recognize.wav_to_text('./text.wav')
    print "Text back: ", text
    this_user.voice_query = text
    db.session.commit()

    return ""


@app.route('/speak_webpage')
def speak_webpage():
    t = Tropo()
    url = request.args.get('url', 'http://en.wikipedia.org') # TODO (temporary for testing): replace wikipedia url with None
    if url:
        t.say("Server error: No URL specified.")
    else:
        webpage = extract.ParsedWebpage(url)
        t.say(webpage.text)

    return t.RenderJson()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)
