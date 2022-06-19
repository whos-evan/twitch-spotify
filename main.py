import os
from queue import Empty
from dotenv import load_dotenv, find_dotenv

import spotipy
import spotipy.util as util

import twitchio
from twitchio.ext import commands

load_dotenv() # loads the .env env variables

spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

channel = os.environ.get("CHANNEL")
prefix = os.environ.get("PREFIX")
access_token = os.environ.get("ACCESS_TOKEN")

sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(client_id=spotify_client_id,
                                               client_secret=spotify_client_secret,
                                               redirect_uri="http://localhost:8080/callback",
                                               scope="user-modify-playback-state"))


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=access_token, prefix=prefix, initial_channels=[f'{channel}'])

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        
    @commands.command()
    @commands.cooldown(rate=1, per=120, bucket=commands.Bucket.user)
    async def rq(self, ctx: commands.Context, *, song: str = None):
        if song is None:
            await ctx.send(f"{ctx.author.name} Command format is `{prefix}rq <song> | <artist>` or `{prefix}rq <song>` or `{prefix}rq <spotify_url>`")
            return
        
        stream = await self.fetch_streams(user_logins=[f'{channel}'])
        if stream:
            try:
                if 'https://open.spotify.com/track/' in song:
                    result = sp.track(song)
                    name = result['name']
                    artist = result['artists'][0]['name']
                    sp.add_to_queue(song)
                else:
                    if '|' in song:
                        song = song.split('|')
                        result = sp.search(q=f'track:{song[0]},artist:{song[1]}', type='track,artist', limit=1)
                    else:
                        result = sp.search(q=f'track:{song}', type='track,artist', limit=1)
                    name = result['tracks']['items'][0]['name']
                    artist = result['tracks']['items'][0]['artists'][0]['name']
                    sp.add_to_queue(result['tracks']['items'][0]['id'])

                await ctx.send(f'{ctx.author.name} Added {name} by: {artist} to the queue!')
            except Exception as e:
                print(f'Error: {e}')
                await ctx.send(f'{ctx.author.name} requested a song that I could not find!')
        else:
            await ctx.send(f"{ctx.author.name} You cannot hijack the streamers queue while the streamer isn't streaming!")

bot = Bot()
bot.run()
