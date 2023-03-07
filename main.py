import os
from typing import Dict, List
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import uvicorn

load_dotenv()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.urandom(64), session_cookie="session")


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: float
    token_type: str


spotify_scope = "playlist-read-private"

sp_oauth = SpotifyOAuth(scope=spotify_scope)


@app.get("/")
async def root():
    return RedirectResponse(url="/login")


@app.get("/playlists", response_class=HTMLResponse)
async def playlists(request: Request):
    if "token_info" not in request.session:
        return RedirectResponse(url="/login")

    token_info = TokenInfo(**request.session["token_info"])
    spotify = get_spotify(token_info)
    playlist_info = get_playlists_info(spotify, spotify.current_user_playlists()['items'])

    return JSONResponse(content=playlist_info)


def get_spotify(token_info: TokenInfo) -> spotipy.Spotify:
    if not sp_oauth.validate_token(token_info.dict()):
        sp_oauth.refresh_access_token(token_info.refresh_token)
    return spotipy.Spotify(auth=token_info.access_token)


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    if "token_info" in request.session:
        return RedirectResponse(url="/playlists")

    auth_url = sp_oauth.get_authorize_url()
    return f'<h2><a href="{auth_url}">Sign in</a></h2>'


@app.get("/logout")
async def logout(request: Request, response: Response):
    request.session.pop("token_info", None)
    response.headers["location"] = "/login"
    response.status_code = 303


@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if code:
        token_info = sp_oauth.get_cached_token()
        request.session["token_info"] = token_info
        response = HTMLResponse(content="<h2>Login successful!</h2>")
        response.headers["location"] = "/playlists"
        response.status_code = 303
    else:
        response = HTMLResponse(content="<h2>Login failed.</h2>")
    return response


def show_login_link() -> str:
    auth_url = sp_oauth.get_authorize_url()
    return f'<h2><a href="{auth_url}">Sign in</a></h2>'


def get_playlists_info(spotify: spotipy.Spotify, playlists: List[Dict]) -> Dict[int, Dict]:
    ret = {}
    for i, playlist in enumerate(playlists):
        ret[i] = spotify.playlist(
            playlist["id"],
            fields="images,name,tracks.items(track(name))",
        )
    return ret


def show_playlists(playlists_info: Dict[int, Dict]) -> str:
    html = "<h2>My playlists:</h2>"
    for _, playlist in playlists_info.items():
        html += f"<h3>{playlist['name']}</h3>"
        html += "<ul>"
        for track in playlist["tracks"]["items"]:
            html += f"<li>{track['track']['name']}</li>"
        html += "</ul>"
    return html


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
