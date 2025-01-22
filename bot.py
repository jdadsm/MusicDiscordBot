import discord
from discord.ext import commands
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Spotify setup
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_SPOTIFY_CLIENT_ID", client_secret="YOUR_SPOTIFY_CLIENT_SECRET"))

# YouTube setup
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def play(ctx, *, query):
    if 'spotify.com' in query:
        # Handle Spotify link
        track_id = query.split('/')[-1]
        track_info = sp.track(track_id)
        search_query = f"{track_info['name']} {track_info['artists'][0]['name']}"
    elif 'youtube.com' in query or 'youtu.be' in query:
        # Handle YouTube link
        search_query = query
    else:
        # Handle general search query
        search_query = query

    # Extract audio URL using youtube_dl
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search_query}", download=False)['entries'][0]
        url = info['formats'][0]['url']

    # Connect to voice channel and play audio
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        voice_client.play(discord.FFmpegPCMAudio(url))
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

bot.run('YOUR_DISCORD_BOT_TOKEN')
