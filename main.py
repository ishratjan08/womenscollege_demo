from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="front_end/static"), name="static")
templates = Jinja2Templates(directory="front_end/templates")

from controllers.query_controller import router as chat
from controllers.import_controller import  router as imp
app.include_router(chat,prefix="/api")
app.include_router(imp,prefix="/api")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})