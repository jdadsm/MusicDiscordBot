import os
import sys
import yt_dlp
import asyncio
import discord

async def search(query:str):
    ydl_opts = {
        'default_search': 'ytsearch',  # Use YouTube search
        'ignoreerrors': True,  # Ignore any errors during extraction
        'quiet': True,  # Suppress console output
        'logtostderr': False,
        'no_warnings': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:    
        if "youtube.com/watch" in query or "youtu.be/" in query:
            try:
                # Extract video info directly from the URL
                info = ydl.extract_info(query, download=False)
                if not info:
                    raise Exception("Invalid URL")
                return info.get('webpage_url'), info.get('title')
            except Exception as e:
                print(f"Error extracting info from URL: {e}")
                return None, None
        else:
            try:
                # Use ytsearch for non-URL queries
                search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)
                
                # If no results were found
                if not search_results or 'entries' not in search_results or not search_results['entries']:
                    return None, None
                
                # Return the first entry
                first_result = search_results['entries'][0]
                return first_result['webpage_url'], first_result['title']
            except Exception as e:
                print(f"Error searching query: {e}")
                return None, None
    
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
            'source_address': '0.0.0.0',
            'postprocessors': []
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
    return await YTDLSource.from_url(url, loop=asyncio.get_event_loop(), stream=True)
