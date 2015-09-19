import os
from flask import Flask, Response, request, url_for
from tropo import Tropo 

app = Flask(__name__)


@app.route('/home/', methods=['GET', 'POST'])
def home():
    t = Tropo()
    t.record(
        name='myrecording',
        say='speech recognition demo',
        transcription={'id': '1234', 'url':'mailto:fephsun@gmail.com'},
        url='http://blah.com',
    )
    return t.RenderJson()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)