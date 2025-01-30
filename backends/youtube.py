import os
import sys
import yt_dlp
import asyncio
import discord

async def search(query:str, count:int=5):
    ydl_opts = {
        'default_search': 'ytsearch',  # Use YouTube search
        'ignoreerrors': True,  # Ignore any errors during extraction
        'quiet': True  # Suppress console output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)
    
    # Return the url and title of the first entry of the results 
    return search_results['entries'][0]['webpage_url'], search_results['entries'][0]['title']

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.url = data.get('url')
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        yt_dlp.utils.bug_reports_message = lambda: ''
        ydl_opts = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        ffmpeg_options = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }
        if os.name == 'nt': # running in Windows
            # Use the ffmpeg Windows build
            if getattr(sys, 'frozen', False):  # Check if running as a bundled executable
                base_path = sys._MEIPASS  # Temporary folder where PyInstaller extracts files
            else:
                base_path = os.path.abspath(".")

            ffmpeg_options['executable'] = os.path.join(base_path, "external", "ffmpeg", "ffmpeg.exe")
            
        ytdl = yt_dlp.YoutubeDL(ydl_opts)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.sanitize_info(ytdl.extract_info(url, download=not stream)))
        if 'entries' in data:
            # take first item from a youtube playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


async def getstream(url: str):
    return await YTDLSource.from_url(clean_youtube_url(url), loop=asyncio.get_event_loop(), stream=True)

from urllib.parse import urlparse, parse_qs, urlencode

def clean_youtube_url(url):
    parsed_url = urlparse(url)
    
    # Ensure it's a YouTube watch URL
    if parsed_url.netloc not in ["www.youtube.com", "youtube.com"]:
        raise ValueError("The provided URL is not a valid YouTube URL.")
    if parsed_url.path != "/watch":
        raise ValueError("The provided URL is not a YouTube video URL.")
    
    # Extract the 'v' parameter (video ID)
    query_params = parse_qs(parsed_url.query)
    if "v" not in query_params:
        raise ValueError("The URL does not contain a valid video ID ('v' parameter).")
    
    video_id = query_params["v"][0]
    
    # Construct and return the clean URL
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    return clean_url