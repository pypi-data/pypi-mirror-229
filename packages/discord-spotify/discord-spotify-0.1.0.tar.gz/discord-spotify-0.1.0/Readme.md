# DISCORD-SPOTIFY

[![Downloads](https://static.pepy.tech/badge/cbvx)](https://pepy.tech/project/cbvx)

A Python package to detailed retrieve Spotify album images for Discord integration.



`example.py`
```py
import discord
from discord.ext import commands
from discord_spotify import spotify

bot = commands.Bot(
    command_prefix=",",
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions.none()
)

@bot.command(name="spotify")
async def spotif(ctx: commands.Context, member: discord.Member = None):
    member = member or ctx.author
    client = spotify.Spotify(bot=bot, member=member)
    content, image, view = await client.get()
    await ctx.reply(content=content, file=image, view=view)

bot.run("token")
```