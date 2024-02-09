from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html = True), name="static" )
