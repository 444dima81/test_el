# main.py

from fastapi import FastAPI

from app.core.config import settings
from app.core.startup import load_vectorstore
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.services.memory import MemoryStore

app = FastAPI(title="ProGit AI Assistant")
app.state.settings = settings
app.state.memory = MemoryStore(k=10)

@app.on_event("startup")
async def startup():
    load_vectorstore(app)

app.include_router(chat_router)
app.include_router(memory_router)
