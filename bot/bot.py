# bot/bot.py

import os
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
BACKEND_API_KEY = os.environ.get("BACKEND_API_KEY", "dev-key")


async def ask_backend(user_id: str, question: str) -> str:
    url = f"{BACKEND_URL}/chat/text"
    headers = {
        "X-API-KEY": BACKEND_API_KEY,
        "X-USER-ID": str(user_id),
    }
    params = {"question": question}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, params=params, timeout=60) as resp:
            if resp.status != 200:
                text = await resp.text()
                return f"Backend error {resp.status}: {text}"
            data = await resp.json()

    answer = data.get("answer") or "Пустой ответ."
    sources = data.get("sources") or []
    if sources:
        # компактно 1–2 источника
        src_lines = []
        for s in sources[:2]:
            src_lines.append(f"- {s.get('heading')} ({s.get('source_file')})")
        answer += "\n\nИсточники:\n" + "\n".join(src_lines)

    return answer


bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Задай вопрос по Git (по базе ProGit).")


@dp.message(F.text)
async def handle_text(message: Message):
    q = (message.text or "").strip()
    if not q:
        return
    await message.chat.do("typing")
    answer = await ask_backend(str(message.from_user.id), q)
    await message.answer(answer)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())