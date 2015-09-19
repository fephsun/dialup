import os
import logging
import random
from flask import Flask, Response, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from tropo import Tropo 

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
    )
    t.on(event='continue', next='/success')
    t.on(event='incomplete', next='/incomplete')
    t.on(event='error', next='/error')
    return t.RenderJson()

@app.route('/success')
def success():
    t = Tropo()
    t.say('Success')
    return t.RenderJson()

@app.route('/incomplete')
def incomplete():
    t = Tropo()
    t.say('incomplete')
    return t.RenderJson()

@app.route('/error')
def error():
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
    this_user.voice_query = audio
    db.session.commit()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)