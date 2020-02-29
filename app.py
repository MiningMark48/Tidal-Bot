import os
import bot
from threading import Thread
from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template
from requests_oauthlib import OAuth2Session
from util.flask_util import check_id


from views.login import login, make_session
from views.dash_overview import dash_overview

t = Thread(target=bot.run)
t.start()
tb = bot.bot

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

app.register_blueprint(dash_overview, url_prefix="/dashboard")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/servers/')
def servers():
    discord = make_session(token=session.get('oauth2_token'))
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    mutual = filter(filter_bot_servs, guilds)

    return render_template("servers.html", servers=mutual)


@app.route('/dashboard/')
def dashboard_index():
    return redirect(url_for("servers"))


@app.route('/dashboard/<serv>/manage/')
def management(serv):
    guild = check_id(serv)
    if guild:
        return render_template("dash_management.html", server=guild)
    else:
        return redirect(url_for("dashboard_index"))


@app.route('/callback')
def callback():
    return redirect("/login/callback")


def filter_bot_servs(serv):
    ids = []
    for s in tb.guilds:
        ids.append(str(s.id))
    return str(serv['id']) in ids


# def check_id(id):
#     discord = make_session(token=session.get('oauth2_token'))
#     guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
#     for guild in guilds:
#         if str(guild['id']) == str(id):
#             return guild
#     return None


if __name__ == '__main__':
    app.run(debug=False)
