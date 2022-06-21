import os
from queue import Empty
from dotenv import load_dotenv, find_dotenv

from datetime import datetime

import spotipy
import spotipy.util as util

import twitchio
from twitchio.ext import commands

import asyncio

load_dotenv() # loads the .env env variables

spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

channel = os.environ.get("CHANNEL")
prefix = os.environ.get("PREFIX")
access_token = os.environ.get("ACCESS_TOKEN")

sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(client_id=spotify_client_id,
                                               client_secret=spotify_client_secret,
                                               redirect_uri="http://localhost:8080/callback",
                                               scope="user-modify-playback-state,user-read-currently-playing"))


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
    @commands.cooldown(rate=1, per=1, bucket=commands.Bucket.user)
    async def sq(self, ctx: commands.Context, *, song: str = None):
        if song is None:
            await ctx.send(f"{ctx.author.name} Command format is `{prefix}sq <song> [number]` or `{prefix}sq <spotify_url>`")
            return
        
        stream = await self.fetch_streams(user_logins=[f'HasanAbi'])
        if stream:
            try:
                now = datetime.now()

                def return_song_choice(result):
                    songs = []
                    ids = []
                    for i in range(len(result['tracks']['items'])):
                        name = result['tracks']['items'][i]['name']
                        artist = result['tracks']['items'][i]['artists'][0]['name']
                        songs.append(f'{str(i)}. {name} - {artist}')
                        ids.append(result['tracks']['items'][i]['id'])
                    choices = ' | '.join(songs)
                    return choices, ids, songs

                if 'https://open.spotify.com/track/' in song:
                    sp.add_to_queue(result['tracks']['items'][0]['id'])
                    name = result['tracks']['items'][0]['name']
                    artist = result['tracks']['items'][0]['artists'][0]['name']
                    await ctx.reply(f'Added {name} by: {artist} to the queue!')

                    current_time = now.strftime("%H:%M:%S")
                    print(f'{ctx.author.name} Added {name} by {artist} to the queue at {current_time}!')
                else:
                    result = sp.search(q=f'track:{song}', type='track,artist', limit=4)
                    if result['tracks']['total'] != 0:
                        choices, ids, songs = return_song_choice(result)
                        
                        await ctx.reply(f'{choices} - Please reply with your choice in 30 seconds.')

                        def check(m):
                            return m.author.name == ctx.author.name and int(m.content) in range(len(songs))
                        try:
                            response = await self.wait_for(event='message', timeout=30.0, predicate=check)

                            for i in range(len(ids)):
                                if response[0].content == str(i):
                                    sp.add_to_queue(ids[i])
                                    await ctx.reply(f'Added {songs[i]} to the queue!')
                            
                            print(f'{ctx.author.name} Added {songs[int(response[0].content)]} to the queue!')
                        except asyncio.TimeoutError:
                            return
                    else:
                        await ctx.reply(f'No results found for {song}.')
            except Exception as e:
                print(f'Error: {e}')
                await ctx.send(f'{ctx.author.name} requested a song that I could not find!')
        else:
            await ctx.send(f"{ctx.author.name} Error! Either the streamer is not currently playing anything on Spotify or is not streaming.")

    @commands.command()
    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.user)
    async def song(self, ctx: commands.Context):
        stream = await self.fetch_streams(user_logins=[f'{channel}'])
        if stream:
            try:
                result = sp.current_user_playing_track()
                await ctx.send(f'{ctx.author.name} Currently playing: {result["item"]["name"]} by {result["item"]["artists"][0]["name"]}')
            except Exception as e:
                print(f'Error: {e}')
                await ctx.send(f'{ctx.author.name} Error fetching current song!')
        else:
            await ctx.send(f"{ctx.author.name} You may not use this command while the streamer isn't streaming!")
    
    @commands.command()
    async def skip(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            sp.next_track()
            await ctx.send(f'{ctx.author.name} Skipped the current song!')


bot = Bot()
bot.run()
