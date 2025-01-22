import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

class SpotifyProcessor:
    def __init__(self):
        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    def get_search_query(self, spotify_url):
        track_id = spotify_url.split('/')[-1]
        track_info = self.sp.track(track_id)
        return f"{track_info['name']} {track_info['artists'][0]['name']}"
