import copy

import discord
import tweepy
from discord.ext import commands, tasks

from util import BotConfig, delete_original
from util.data.guild_data import GuildData

# These are tweets waiting to be sent, due to one function being async and the other not,
# it must be stored temporarily in a dictionary variable
queued_tweets = {}


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self, data, webhooks):
        self.data = data
        self.webhooks = webhooks

        super().__init__()

    def on_status(self, status):
        if not self.from_creator(status):
            return

        if str(status.text).startswith("RT @"):
            return

        try:
            for channel in self.data[status.user.id_str]:
                webhook = self.webhooks[channel]
                user = status.user

                embed = discord.Embed(title=f"{user.name} (@{user.screen_name})", url=user.url, color=0x08A0E9)
                embed.description = f"{status.text}\n[Link](https://twitter.com/twitter/statuses/{status.id})"
                embed.set_thumbnail(url=user.profile_image_url_https)
                embed.timestamp = status.created_at
                embed.set_footer(text=status.source)
                # await webhook.send(embed=embed, username="Twitter")

                queued_tweets.update({embed: webhook})
        except KeyError:
            return

    def on_error(self, code):
        if code == 420:
            return False
        return True

    @staticmethod
    def from_creator(status):
        if hasattr(status, 'retweeted_status'):
            return False
        elif status.in_reply_to_status_id is not None:
            return False
        elif status.in_reply_to_screen_name is not None:
            return False
        elif status.in_reply_to_user_id is not None:
            return False
        else:
            return True


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.webhook_name = "tb-twitter"
        self.auth = self.setup_tweepy_auth()
        self.api = tweepy.API(self.auth)
        self.stream = None
        self.webhooks = {}

        self.dispatcher.start()

    @tasks.loop(seconds=15)
    async def dispatcher(self):
        for tweet in queued_tweets:
            webhook = queued_tweets[tweet]
            await webhook.send(embed=tweet, username=f"Twitter",
                               avatar_url="https://f000.backblazeb2.com/file/miningmark48-files/Twitter_Logo_Blue.png")
        queued_tweets.clear()

    @dispatcher.before_loop
    async def before_dispatcher(self):
        await self.bot.wait_until_ready()

    @staticmethod
    def setup_tweepy_auth():
        config = BotConfig()
        consumer_key = config.get_api_key('twitter_consumer_key')
        consumer_secret = config.get_api_key('twitter_consumer_secret')
        access_token = config.get_api_key('twitter_access_token')
        access_token_secret = config.get_api_key('twitter_access_token_secret')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth

    def setup_tweepy_stream(self, stream_data):
        listener = TwitterStreamListener(stream_data, self.webhooks)
        return tweepy.Stream(auth=self.auth, listener=listener)

    def prep_stream(self):
        stream_data = {}
        connected_guilds = self.bot.guilds
        for guild in connected_guilds:
            data = GuildData(str(guild.id)).twitter_follows.fetch_all()
            for user in data:
                if user[1] in stream_data:
                    stream_data.update({user[1]: stream_data[user[1]].append(user[2])})
                else:
                    stream_data.update({user[1]: [user[2]]})

        return stream_data

    async def prep_webhooks(self, data):
        webhooks = {}
        for user in data:
            for channel_id in data[user]:

                channel = self.bot.get_channel(int(channel_id))
                webhook = discord.utils.find(lambda w: (isinstance(w, discord.Webhook) and w.name == self.webhook_name),
                                             await channel.webhooks())
                if not webhook:
                    webhook = await channel.create_webhook(name=self.webhook_name, reason="Twitter Follow")

                webhooks.update({channel_id: webhook})

        return webhooks

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        stream_data = self.prep_stream()
        self.webhooks = await self.prep_webhooks(stream_data)
        self.stream = self.setup_tweepy_stream(stream_data)
        self.stream.filter(follow=[user for user in stream_data], is_async=True)

    @commands.group(aliases=["twit", "youtwit"])
    @commands.has_permissions(manage_guild=True)
    async def twitter(self, ctx):
        """
        [Experimental] Allows a server manager to follow users on Twitter, creating a feed in a channel
        """

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @twitter.command(name="follow", aliases=["fol"])
    @commands.cooldown(3, 2, commands.BucketType.user)
    @delete_original()
    async def twitter_follow(self, ctx, username: str):
        """
        Follow a user to get Tweets from
        """

        try:
            user = self.api.get_user(username)
        except tweepy.TweepError:
            return await ctx.send("Invalid username!")

        user_id = user.id_str
        guild_data = GuildData(str(ctx.guild.id)).twitter_follows
        if guild_data.fetch_by_name(user_id):
            return await ctx.send(f"You're already following **{username}**!", delete_after=5)
        guild_data.set(user_id, str(ctx.channel.id))
        await self.on_ready()

        await ctx.send(f"Now following **{username}**!\n\t`ID: {user_id}`", delete_after=5)

    @twitter.command(name="unfollow", aliases=["ufol"])
    @commands.cooldown(3, 2, commands.BucketType.user)
    @delete_original()
    async def twitter_unfollow(self, ctx, username: str):
        """
        Unfollow a user so Tweets are no longer received
        """

        try:
            user = self.api.get_user(username)
        except tweepy.TweepError:
            return await ctx.send("Invalid username!")

        user_id = str(user.id_str)
        guild_data = GuildData(str(ctx.guild.id)).twitter_follows

        if not guild_data.fetch_by_name(user_id):
            return await ctx.send(f"You're not following **{username}**!", delete_after=5)

        guild_data.delete(user_id)
        await self.on_ready()

        await ctx.send(f"Unfollowed **{username}**!\n\t`ID: {user_id}`", delete_after=5)

    @twitter.command(name="following", aliases=["list"])
    @commands.cooldown(3, 2, commands.BucketType.user)
    @delete_original()
    async def twitter_following(self, ctx):
        """
        Get a list of all current Twitter users being followed
        """

        following = GuildData(str(ctx.guild.id)).twitter_follows.fetch_all()
        if following:
            following_names = ', '.join(f"@{self.api.get_user(int(user[1])).screen_name}" for user in following)
        else:
            following_names = "No one :("

        await ctx.send(f"**Following:** {following_names}")


def setup(bot):
    bot.add_cog(Utility(bot))
