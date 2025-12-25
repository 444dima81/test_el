# mini_clean_book.py
from pathlib import Path
import re

INP = Path("pro_git_ru.txt")
OUT = Path("pro_git_ru.cleaned.txt")

text = INP.read_text(encoding="utf-8")

# Вырезаем код-блоки
code_blocks = []

def _stash_code(m):
    code_blocks.append(m.group(0))
    return f"@@CODE_BLOCK_{len(code_blocks)-1}@@"

text = re.sub(
    r"\[source\]\s*\n----\n.*?\n----",
    _stash_code,
    text,
    flags=re.DOTALL
)

# Чистим обычный текст
text = re.sub(r"(?m)^\s*\[\[[^\]]+\]\]\s*$", "", text)
text = re.sub(r"\(\(\([^)]+\)\)\)", "", text)
text = re.sub(r"(?m)^\s*:[\w\-]+:.*$", "", text)
text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

# Возвращаем код-блоки
for i, block in enumerate(code_blocks):
    text = text.replace(f"@@CODE_BLOCK_{i}@@", block)

OUT.write_text(text, encoding="utf-8")
print(f"Готово: {OUT}")