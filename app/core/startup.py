# startup.py

from fastapi import FastAPI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings


def load_vectorstore(app: FastAPI) -> None:
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.HF_MODEL_NAME,
        model_kwargs={"device": "mps"},  
        encode_kwargs={"normalize_embeddings": True},
    )

    vectorstore = FAISS.load_local(
        str(settings.FAISS_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    app.state.vectorstore = vectorstore