# retrieval.py

from typing import List
from langchain_core.documents import Document


def normalize_query(q: str) -> str:
    ql = q.lower()
    if ql.startswith(("что такое", "что значит", "объясни")):
        q = q + " определение"
    if "rebase" in ql and "git" not in ql:
        q = "git " + q
    return "query: " + q


def is_core_git(md: dict) -> bool:
    sf = (md.get("source_file") or "").lower()
    if any(x in sf for x in ["other-scms", "svn", "bzr", "p4"]):
        return False
    if any(x in sf for x in ["book/06-github/", "book/04-git-server/sections/gitlab"]):
        return False
    return True

def heading_rank_for_rebase(heading: str | None) -> int:
    h = (heading or "").lower()
    # чем меньше число — тем выше приоритет
    if h == "перебазирование":
        return 0
    if "простейшее" in h:
        return 1
    if "интерактив" in h:
        return 2
    if "перемещение vs" in h or "сравнение" in h:
        return 9
    return 5

def prefer_rebase(md: dict) -> bool:
    sf = (md.get("source_file") or "").lower()
    return "sections/rebasing.asc" in sf


def is_rebase_doc(md: dict) -> bool:
    sf = (md.get("source_file") or "").lower()
    return "book/03-git-branching/sections/rebasing.asc" in sf


def retrieve(vectorstore, query: str, k: int = 3) -> List[Document]:
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 50, "lambda_mult": 0.2},
    )

    q_norm = normalize_query(query)
    docs = retriever.invoke(q_norm)
    docs = [d for d in docs if is_core_git(d.metadata)]

    ql = query.lower()
    if ("rebase" in ql) or ("перебаз" in ql):
        # 1) поднимаем кандидатов из rebasing.asc
        docs.sort(key=lambda d: 0 if prefer_rebase(d.metadata) else 1)

        # 2) если есть каноничная секция — оставляем только её
        reb = [d for d in docs if is_rebase_doc(d.metadata)]
        if reb:
            docs = reb

        # 3) если вопрос дефиниционный — ранжируем по заголовку (хотим "Перебазирование" первым)
        if ql.startswith(("что такое", "что значит", "объясни")):
            docs.sort(key=lambda d: heading_rank_for_rebase(d.metadata.get("heading")))

        # 4) для rebase обычно полезно вернуть 3 кусочка (определение + принцип + пример)
        k = max(k, 3)

    return docs[:k]