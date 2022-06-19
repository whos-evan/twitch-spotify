# twitch-spotify
Allows users to queue Spotify songs using twitch commands. Uses Python (twitchio and spotipy).

## Commands:
There is one command ``?rq`` however it has different ways that you can use it:
- ``?rq <song | artist>``
- ``?rq <song>``
- ``?rq <spotify url>``

To prevent spammers there is a 120 second cooldown, there is also a check to ensure that the streamer is live before you can make a song request.

## To get started:
1. Copy the ``example.env`` file and rename it to ``.env``.
2. Go to https://developer.spotify.com/dashboard/applications and create an application. Ensure that you set the redirect url to ``http://localhost:8080/callback``
3. Copy the client id and client secret and paste them into a ``.env`` file.
4. Go to https://twitchtokengenerator.com/ and generate your token.
5. Set the prefix and channel that you want to join.
6. Install the ``requirements.txt``
7. Run the program!
8. Have fun getting DMCAed!


## About DMCA...
> I do not promote streaming content that you do not have the rights to stream. If you use this program to stream content that you do not own you will likely face punishment. Use at your own risk.
