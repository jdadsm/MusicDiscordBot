import discord
import logging
import os
from discord.ext import commands
from backends.youtube import getstream ,search
from backends.spotify import SpotifyProcessor

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix='$', intents=intents)

song_queue = {}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"Message received in {message.channel.name}: {message.content}")

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def play(ctx, *, query):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You need to be in a voice channel to use this command.")
            return

    url, title = await search(query)

    if ctx.guild.id not in song_queue:
        song_queue[ctx.guild.id] = []

    song_queue[ctx.guild.id].append({'url': url, 'title': title})

    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(f"Added to queue: {title}")

async def play_next(ctx):
    if ctx.guild.id in song_queue and song_queue[ctx.guild.id]:
        next_song = song_queue[ctx.guild.id].pop(0)
        ctx.voice_client.play(await getstream(next_song['url']), after=lambda e: bot.loop.create_task(check_queue(ctx)))
        await ctx.send(f"Now playing: {next_song['title']}")
    else:
        await ctx.voice_client.disconnect()

async def check_queue(ctx):
    if ctx.guild.id in song_queue and song_queue[ctx.guild.id]:
        await play_next(ctx)
    else:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Queue is empty. Disconnecting from voice channel.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        if ctx.guild.id in song_queue:
            song_queue[ctx.guild.id].clear()
        await ctx.send("Stopped playing and cleared the queue.")
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No song is currently playing.")

@bot.command()
async def queue(ctx):
    if ctx.guild.id in song_queue and song_queue[ctx.guild.id]:
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(song_queue[ctx.guild.id])])
        await ctx.send(f"Current queue:\n{queue_list}")
    else:
        await ctx.send("The queue is empty.")

bot.run(DISCORD_BOT_TOKEN)
