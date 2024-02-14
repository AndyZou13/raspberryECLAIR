from flash import Flask
from starlette.responses import FileResponse 
from fastapi.staticfiles import StaticFiles

app = Flask(__name__)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")