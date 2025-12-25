# build_faiss.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

INP_JSONL = PROJECT_DIR / "data" / "progit_docs.jsonl"
OUT_DIR = PROJECT_DIR / "vectorize" / "store_faiss"

HF_MODEL_NAME = "intfloat/multilingual-e5-large"


def load_docs_jsonl(path: Path) -> List[Document]:
    docs: List[Document] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            docs.append(Document(page_content=obj["page_content"], metadata=obj.get("metadata", {})))
    return docs


def build_faiss():
    docs = load_docs_jsonl(INP_JSONL)
    print(f"Загружено секций: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1400,
        chunk_overlap=220,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = splitter.split_documents(docs)
    print(f"После дочанковки чанков: {len(chunks)}")

    
    for d in chunks:
        d.page_content = "passage: " + d.page_content

    embeddings = HuggingFaceEmbeddings(
    model_name=HF_MODEL_NAME,
    model_kwargs={"device": "mps"},
    encode_kwargs={"normalize_embeddings": True, "batch_size": 32},
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(OUT_DIR, exist_ok=True)
    vectorstore.save_local(str(OUT_DIR))
    print(f"FAISS сохранён в: {OUT_DIR}")


if __name__ == "__main__":
    build_faiss()


# Загружено секций: 453
# После дочанковки чанков: 892