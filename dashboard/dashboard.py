from discord import channel
from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc

app = Quart(__name__)
ipc_client = ipc.Client(secret_key="MM")

app.config["SECRET_KEY"] = "MM"
app.config["DISCORD_CLIENT_ID"] = 682756052126924810
app.config["DISCORD_CLIENT_SECRET"] = "-_6_brtZIWPu3r6HejYy5G0D0mc81BSQ"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

discord = DiscordOAuth2Session(app)

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
	return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET"])
async def dashboard():
	guild_count = await ipc_client.request("get_guild_count")
	guild_ids = await ipc_client.request("get_guild_ids")

	try:
		user_guilds = await discord.fetch_guilds()
	except:
		return redirect(url_for("login")) 

	same_guilds = []

	for guild in user_guilds:
		if guild.id in guild_ids:
			same_guilds.append(guild)


	return await render_template("dashboard.html", guild_count=guild_count, guilds=same_guilds)

@app.route("/guild/<guild_id>")
async def guild(guild_id: int):
	guild_data = next((x for x in await discord.fetch_guilds() if str(x.id) == str(guild_id)), None)
	return await render_template("guild.html", guild=guild_data, channels=await ipc_client.request("get_guild_text_channels", guild_id=guild_id))

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