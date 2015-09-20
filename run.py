import sys, os
import logging
import random
from flask import Flask, Response, request, url_for, send_file
from flask.ext.sqlalchemy import SQLAlchemy
from tropo import Tropo, Choices

import extract
import recognize

# Log all the bad things.
root = logging.getLogger()
log = logging.StreamHandler(sys.stdout)
log.setLevel(logging.DEBUG)
root.addHandler(log)

# A magic string for bad queries...
BAD_QUERY = "BAD_QUERY"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    voice_query = db.Column(db.Text())

    def __repr__(self):
        return '<User id %d>' % self.userid

def im_feeling_lucky(query):
    google_url = "http://www.google.com/search?q=%s&btnI"
    return google_url % query

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
        say="What website to visit? Speak your query for an I'm Feeling Lucky Google search.",
        choices={'terminator': '#'},
        url='http://infinite-cove-6526.herokuapp.com/record?userid={0}' \
            .format(userid),
        asyncUpload=True,
        maxTime=10,
        maxSilence=3,
    )
    t.on(event='continue', next='/wait_for_recog?userid={0}'.format(userid))
    t.on(event='incomplete', next='/home')
    t.on(event='error', next='/home')
    return t.RenderJson()

@app.route('/wait_for_recog', methods=['GET', 'POST'])
def wait_for_recog():
    print "wait_for_recog"
    userid = int(request.args['userid'])
    t = Tropo()
    user = User.query.filter_by(userid=userid).first()
    if user.voice_query == BAD_QUERY:
        print "Bad query"
        t.say("We couldn't understand you.")
        t.on(event='continue', next='/home')
    elif len(user.voice_query) > 0:
        print "Query-get!"
        t.say("Your query was " + user.voice_query)
        t.on(event='continue', next='/speak_webpage?userid={0}'.format(userid))
    else:
        print "loading"
        t.say("Loading")
        t.on(event='continue', next='/wait_for_recog?userid={0}'.format(userid))
    debug_json = t.RenderJson()
    return debug_json

@app.route('/record', methods=['GET', 'POST'])
def record():
    print "Recording received!"

    userid = int(request.args['userid'])
    print "User: ", userid
    this_user = User.query.filter_by(userid=userid).first()

    audio = request.files['filename'].read()
    print "Audio file size: ", len(audio)
    wav_filename = '/tmp/test{0}.wav'.format(userid)
    out_file = open(wav_filename, 'wb')
    out_file.write(audio)

    # Test speech recognition
    text = recognize.wav_to_text(wav_filename)
    if text is None:
        text = BAD_QUERY
    print "Text back: ", text
    this_user.voice_query = text
    db.session.commit()

    return ""


@app.route('/speak_webpage', methods=['GET', 'POST'])
def speak_webpage():
    print "speak_webpage"
    t = Tropo()
    userid = request.args.get('userid', None)
    if userid is None:
        t.say("No user specified. Error.")
        return t.RenderJson()
    userid = int(userid)
    user = User.query.filter_by(userid=userid).first()
    print "found user"

    url = im_feeling_lucky(user.voice_query)
    print "got url"

    webpage = extract.ParsedWebpage(url)
    print "got webpage"
    # t.say(webpage.text)
    t.ask(Choices('[1-4 DIGITS]'),
        say=webpage.text,
        bargein=False,
        onChoice=lambda event: say(str(event)))
    print "done"
    return t.RenderJson()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)
