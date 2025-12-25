# test_retrieval.py
from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent.parent
STORE_DIR = PROJECT_DIR / "vectorize" / "store_faiss"

HF_MODEL_NAME = "intfloat/multilingual-e5-large"


def normalize_query(q: str) -> str:
    ql = q.lower()
    if "rebase" in ql and "git" not in ql:
        q = "git " + q
    return "query: " + q


def strip_passage(text: str) -> str:
    if text.startswith("passage: "):
        return text[len("passage: "):]
    return text


def main():
    embeddings = HuggingFaceEmbeddings(
        model_name=HF_MODEL_NAME,
        model_kwargs={"device": "mps"},   
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": 32,
        },
    )

    vs = FAISS.load_local(
        str(STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    retriever = vs.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 6,
            "fetch_k": 30,
            "lambda_mult": 0.4,
        },
    )

    queries = [
        "что такое rebase",
        "чем отличается merge от rebase",
        "как отменить последний коммит",
        "что такое staging area",
    ]

    for q in queries:
        print("\n" + "=" * 100)
        print("Q:", q)

        q_norm = normalize_query(q)
        results = retriever.invoke(q_norm)

        for i, d in enumerate(results, 1):
            md = d.metadata
            title = (
                f"{md.get('chapter_file')} | "
                f"{md.get('source_file')} | "
                f"{md.get('heading')}"
            )
            print(f"\n#{i} {title}")
            print(strip_passage(d.page_content)[:500])


if __name__ == "__main__":
    main()