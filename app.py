import os
from dotenv import load_dotenv
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./.flask_session/"
Session(app)

load_dotenv()


@app.route("/")
def login():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope="playlist-read-private", cache_handler=cache_handler
    )

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        all_playlists = spotify.current_user_playlists()
        ret = dict()

        for i in range(len(all_playlists["items"])):
            ret[i] = spotify.playlist(
                all_playlists["items"][i]["id"],
                fields="images,name,tracks.items(track(name,preview_url,album(images)))",
            )
        return ret

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'


@app.route("/sign_out")
def sign_out():
    session.pop("token_info", None)
    return redirect("/")


"""
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
"""
if __name__ == "__main__":
    app.run(
        threaded=True,
        port=int(
            os.environ.get(
                "PORT", os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1]
            )
        ),
    )
