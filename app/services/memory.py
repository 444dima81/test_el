# services/memory.py
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


class MemoryStore:
    def __init__(self, k: int = 10):
        self.k = k
        self._store: Dict[str, Deque[ChatTurn]] = {}

    def get(self, user_id: str) -> List[ChatTurn]:
        return list(self._store.get(user_id, deque()))

    def append(self, user_id: str, role: str, content: str) -> None:
        q = self._store.setdefault(user_id, deque(maxlen=self.k * 2))
        q.append(ChatTurn(role=role, content=content))

    def clear(self, user_id: str) -> None:
        self._store.pop(user_id, None)