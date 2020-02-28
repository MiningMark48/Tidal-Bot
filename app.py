import os
from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template
from requests_oauthlib import OAuth2Session

from views.login import login


OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
app.register_blueprint(login, url_prefix="/login")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/<serv>/')
def server(serv):
    return render_template("index.html", server_name=serv)


@app.route('/module/')
def module():
    return render_template("module.html")


@app.route('/callback')
def callback():
    return redirect("/login/callback")


if __name__ == '__main__':
    app.run()
