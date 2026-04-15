from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage

from shopping_assistant.workflow.agentic_rag_workflow import AgenticRAG

app = FastAPI()

app.mount("/static", StaticFiles(directory="shopping_assistant/static"), name="static")
templates = Jinja2Templates(directory="shopping_assistant/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get")
async def chat(msg: str = Form(...)):
    rag_agent = AgenticRAG()
    answer = await rag_agent.run(msg)
    return answer