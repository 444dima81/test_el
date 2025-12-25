# ProGit AI Assistant (RAG + FastAPI + Telegram Bot)

Ассистент по Git на основе книги Pro Git (RU) с Retrieval-Augmented Generation:
- OFFLINE: парсинг -> чанки -> embeddings (HF E5) -> FAISS
- ONLINE: FastAPI API -> retrieval -> LLM (GigaChat via OpenAI-compatible API)
- Telegram-бот проксирует сообщения в backend, user_id = Telegram user id (память диалога per user)


## Выполненные работы

### 1. OFFLINE pipeline (база знаний)
- Парсинг Pro Git (RU) с сохранением структуры
- Очистка AsciiDoc и технического шума
- Чанкинг с метаданными (глава, секция, уровень)
- Эмбеддинги: `intfloat/multilingual-e5-large`
- FAISS-векторная база, сохранение на диск
- Отдельный offline-скрипт (без FastAPI)

### 2. Retrieval и фильтрация
- Загрузка FAISS при старте приложения
- MMR-поиск релевантных чанков
- Фильтрация нерелевантных разделов
- Приоритизация канонических секций (`rebasing.asc`)
- Отдельная логика для дефиниционных вопросов

### 3. Контекстная память
- In-memory memory per `user_id`
- Хранение последних `k=10` сообщений
- Использование истории при генерации ответа
- Endpoint очистки памяти пользователя

### 4. Авторизация
- HTTP headers: `X-API-KEY`, `X-USER-ID`
- Проверка ключа на backend’е
- `user_id` используется для memory и диалога

### 5. LLM (GigaChat)
- Интеграция через OpenAI-совместимый API
- Асинхронная генерация ответов
- Ответы строго на основе RAG-контекста
- Корректная обработка отсутствия LLM

### 6. API (FastAPI)
- `POST /chat/text` — RAG + memory
- `POST /memory/clear` — очистка памяти
- Swagger-документация
- Асинхронная архитектура

### 7. Docker
- Dockerfile для backend и бота
- `docker-compose.yml` (backend + bot)
- Конфигурация через `.env`
- Запуск одной командой

### 8. Telegram-бот
- Бот на **aiogram 3**
- `user_id` = Telegram user id
- Проксирование запросов в backend
- Поддержка контекстного диалога


## Стек
- FastAPI + Uvicorn
- LangChain (FAISS vectorstore, retriever)
- Embeddings: `intfloat/multilingual-e5-large`
- Vector DB: FAISS
- LLM: GigaChat
- Telegram bot: aiogram 3

---
