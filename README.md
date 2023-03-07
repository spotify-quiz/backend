# Backend for spotify-quiz

--- NO TEST COVERAGE ---  *not implemented yet. :crying_cat_face:

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`SPOTIPY_CLIENT_ID`
`SPOTIPY_CLIENT_SECRET`
`SPOTIPY_REDIRECT_URI` 

## How to run this locally

Start the server

```bash
  uvicorn main:app --env-file="./env"  
```
Please note that in this case, if you use reload=True or workers=NUM, you should put uvicorn.run into `if __name__ == '__main__'` clause in the main module
```bash
    uvicorn.run("main:app", port=5000, reload=True, access_log=False)
```
```bash
  uvicorn main:app --env-file="./env"  --workers=4
```
You can also use reload but not with workers. For auto-reload. 
```bash
  uvicorn main:app --env-file="./env"  --reload
```

## Tools 
Starlette fo Session, Caching and Cookies
FastAPI for fast docs (OpenAPI)
Uvicorn for ASGI server
Might have to use Gunicorn as well for WSGI (production level)
## Endpoints
Please see localhost:8000/docs to check endpoints
```bash
    localhost:8000/docs
```
