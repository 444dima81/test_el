# app/services/llm_gigachat.py

import asyncio
from openai import OpenAI


SYSTEM_PROMPT = (
    "Ты технический ассистент по Git.\n"
    "Отвечай СТРОГО на основе предоставленного КОНТЕКСТА.\n"
    "Если ответа нет в контексте — скажи: "
    "'В базе знаний нет ответа на этот вопрос.'\n"
    "Пиши кратко, по делу, по-русски."
    'Используй терминологию Git: "коммиты", "ветка", "история".'
)


def _format_history(turns) -> str:
    if not turns:
        return ""
    lines = []
    for t in turns:
        role = "Пользователь" if t.role == "user" else "Ассистент"
        lines.append(f"{role}: {t.content}")
    return "\n".join(lines)


def _sync_generate(
    api_key: str,
    base_url: str,
    model: str,
    question: str,
    context: str,
    history: str,
) -> str:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    user_prompt = f"""
ИСТОРИЯ ДИАЛОГА:
{history}

КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}

ВОПРОС:
{question}

Ответь строго по контексту.
"""

    response = client.chat.completions.create(
        model=model,
        max_tokens=700,
        temperature=0.3,
        top_p=0.9,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content.strip()


async def generate_answer(
    api_key: str,
    base_url: str,
    model: str,
    question: str,
    context: str,
    history_turns,
) -> str:
    history = _format_history(history_turns)

    return await asyncio.to_thread(
        _sync_generate,
        api_key,
        base_url,
        model,
        question,
        context,
        history,
    )