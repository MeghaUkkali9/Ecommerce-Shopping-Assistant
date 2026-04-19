from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from shopping_assistant.workflow.agentic_rag_with_mcp_tools import AgenticRAG

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

from fastapi import Request

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get")
async def chat(msg: str = Form(...)):
    rag_agent = AgenticRAG()
    answer = rag_agent.run(msg)
    return answer