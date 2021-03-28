from sqlalchemy import exc
import toml
import functools
from discord import channel
from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc

config_data = toml.load("config.toml")
config_dash_data = config_data["dashboard"]

app = Quart(__name__)
ipc_client = ipc.Client(secret_key=config_dash_data["secret_key"])

app.config["SECRET_KEY"] = config_dash_data["secret_key"]
app.config["DISCORD_CLIENT_ID"] = config_dash_data["discord_client_id"]
app.config["DISCORD_CLIENT_SECRET"] = config_dash_data["discord_client_secret"]
app.config["DISCORD_REDIRECT_URI"] = config_dash_data["discord_redirect_uri"]

discord = DiscordOAuth2Session(app)

# def ipc_autoreconnect(func):
# 	def inner(*args, **kwargs):
# 		try:
# 			func(*args, **kwargs)
# 		except:
# 			# global ipc_client
# 			# ipc_client = ipc.Client(secret_key=config_dash_data["secret_key"])
# 			print(f"{func.__name__}")

# 	return inner

@app.route("/")
async def home():
	return await render_template("index.html")

@app.route("/login")
async def login():
	return await discord.create_session(scope=["identify", "email", "guilds"])

@app.route("/callback")
async def callback():
	try:
		await discord.callback()
	except:
		return redirect(url_for("login"))

	# user = await discord.fetch_user()
	# return f"{user.name}#{user.discriminator}" #You should return redirect(url_for("dashboard")) here
	return redirect(url_for("manage"))

@app.route("/manage", methods=["GET"])
async def manage():
	guild_count = await ipc_client.request("get_guild_count")
	guild_ids = await ipc_client.request("get_guild_ids")

	try:
		user_guilds = await discord.fetch_guilds()
	except:
		return redirect(url_for("login")) 

	same_guilds = []

	for guild in user_guilds:
		if guild.id in guild_ids and guild.permissions.manage_guild:
			same_guilds.append(guild)
	
	user = await discord.fetch_user()
	user_name = user.username
	user_discriminator = user.discriminator
	user_avatar = user.avatar_url

	user_info = {"name": user_name, "discriminator": user_discriminator, "avatar": user_avatar}

	return await render_template("manage.html", user_info=user_info, guild_count=guild_count, guilds=same_guilds)

@app.route("/guild/<guild_id>", methods=["GET", "POST"])
# @ipc_autoreconnect
async def guild(guild_id: int):

	guild_data = next((x for x in await discord.fetch_guilds() if str(x.id) == str(guild_id)), None)

	if request.method == "POST":
		form = await request.form
		
		if "btn_cmd_prefix_update" in form:
			await ipc_client.request("set_prefix", guild_id=guild_id, prefix=form["text_cmd_prefix"])
		elif "btn_nickname_update" in form:
			await ipc_client.request("set_nickname", guild_id=guild_id, nickname=form["text_nickname"])
		elif "btn_join_msg" in form:
			await ipc_client.request("set_join_msg", guild_id=guild_id, message=form["text_join_msg"])

	render_channels = await ipc_client.request("get_guild_text_channels", guild_id=guild_id)
	render_join_msg = await ipc_client.request("get_join_msg", guild_id=guild_id)
	return await render_template("guild.html", guild=guild_data, channels=render_channels, join_msg=render_join_msg)

@app.route("/guild/<guild_id>/channel/<channel_id>")
async def text_channel(guild_id: int, channel_id: int):
	guild_data = next((x for x in await discord.fetch_guilds() if str(x.id) == str(guild_id)), None)
	channels = await ipc_client.request("get_guild_text_channels", guild_id=guild_id)	
	channel = next((x for x in channels if str(x["id"]) == str(channel_id)), None)

	return await render_template("channel.html", guild=guild_data, channel=channel)

@app.route("/guild/<guild_id>/channel/<channel_id>", methods=["POST"])
async def text_channel_post(guild_id: int, channel_id: int):
	guild_data = next((x for x in await discord.fetch_guilds() if str(x.id) == str(guild_id)), None)
	form = await request.form
	text = form["text"]

	await ipc_client.request("cmd_say", guild_id=guild_id, channel_id=channel_id, message=text)

	return await render_template("channel.html", guild=guild_data, channel=channel)

if __name__ == "__main__":
	app.run(debug=True)
