from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="front_end/static"), name="static")

# Create directories if they don't exist
os.makedirs("outputs", exist_ok=True)
os.makedirs("input_audio", exist_ok=True)

# Serve response audio files
app.mount("/response_audio", StaticFiles(directory="outputs"), name="response_audio")

# Serve input audio files (optional)
app.mount("/input_audio", StaticFiles(directory="input_audio"), name="input_audio")

templates = Jinja2Templates(directory="front_end/templates")

from controllers.query_controller import router as chat
from controllers.import_controller import  router as imp
app.include_router(chat,prefix="/api")
app.include_router(imp,prefix="/api")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})