# chat.py

from fastapi import APIRouter, Request
from langchain_core.documents import Document

from app.api.deps import UserIdDep
from app.services.retrieval import retrieve
from app.services.llm_gigachat import generate_answer

router = APIRouter()

MAX_CHARS_PER_DOC = 800
MAX_DEFINITION_CONTEXT = 1200


def strip_passage(text: str) -> str:
    return text[len("passage: "):] if text.startswith("passage: ") else text


def build_context(question: str, docs: list[Document]) -> str:
    ql = question.lower()

    if ql.startswith(("что такое", "что значит", "объясни")):
        merged = "\n\n".join(strip_passage(d.page_content) for d in docs)
        return merged[:MAX_DEFINITION_CONTEXT]

    return "\n\n".join(
        strip_passage(d.page_content)[:MAX_CHARS_PER_DOC]
        for d in docs
    )


@router.post("/chat/text")
async def chat_text(
    request: Request,
    question: str,
    user_id: str = UserIdDep,
):
    vectorstore = request.app.state.vectorstore
    docs = retrieve(vectorstore, question)

    # Пишем вопрос в память
    request.app.state.memory.append(user_id, "user", question)

    if not docs:
        answer = "В базе знаний нет ответа на этот вопрос."
        request.app.state.memory.append(user_id, "assistant", answer)
        return {
            "question": question,
            "answer": answer,
            "sources": [],
            "user_id": user_id,
        }

    context = build_context(question, docs)

    # GigaChat
    settings = request.app.state.settings
    history = request.app.state.memory.get(user_id)

    if not settings.GIGACHAT_API_KEY:
        answer = "LLM не настроен: отсутствует GIGACHAT_API_KEY."
    else:
        answer = await generate_answer(
            api_key=settings.GIGACHAT_API_KEY,
            base_url=settings.GIGACHAT_BASE_URL,
            model=settings.GIGACHAT_MODEL,
            question=question,
            context=context,
            history_turns=history,
        )

    # Пишем ответ в память
    request.app.state.memory.append(user_id, "assistant", answer)

    return {
        "question": question,
        "answer": answer,
        "sources": [d.metadata for d in docs],
        "user_id": user_id
    }