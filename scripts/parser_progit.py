# parser_progit.py
from pathlib import Path
import re
import json
from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

INP = PROJECT_DIR / "data" / "pro_git_ru.cleaned.txt"
OUT_JSONL = PROJECT_DIR / "data" / "progit_docs.jsonl"

re_chapter = re.compile(r"^===== (.+?) =====\s*$")
re_source  = re.compile(r"^-----\s+(.+?)\s+-----\s*$")
re_heading = re.compile(r"^(=+)\s+(.+?)\s*$")  # == Title, === Title, ==== Title ...
re_image   = re.compile(r"^\s*image::.+\]\s*$")  # image::...["..."]

def parse_to_documents(text: str) -> list[Document]:
    chapter_file = None           
    source_file = "unknown"       
    heading = None                
    level = None                
    buf: list[str] = []

    docs: list[Document] = []

    def flush():
        nonlocal buf, docs
        content = "\n".join(buf).strip()
        if content:
            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "chapter_file": chapter_file,
                        "source_file": source_file,
                        "heading": heading,
                        "level": level,
                    },
                )
            )
        buf = []

    for line in text.splitlines():
        # Глава-скелет
        m = re_chapter.match(line)
        if m:
            flush()
            chapter_file = m.group(1)
            source_file = chapter_file  
            heading = None
            level = None
            continue

        # Реальный файл секции
        m = re_source.match(line)
        if m:
            flush()
            source_file = m.group(1)
            heading = None
            level = None
            continue

        # Заголовки AsciiDoc: ==/===/==== ...
        m = re_heading.match(line)
        if m:
            eqs = m.group(1)
            title = m.group(2).strip()
            # интересуют заголовки уровня >= 2
            if len(eqs) >= 2:
                flush()
                heading = title
                level = len(eqs)
                continue

        # Картинки выкидываем
        if re_image.match(line):
            continue

        buf.append(line)

    flush()
    return docs

def save_jsonl(docs: list[Document], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for d in docs:
            rec = {"page_content": d.page_content, "metadata": d.metadata}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    text = INP.read_text(encoding="utf-8")
    docs = parse_to_documents(text)

    print(f"Документов (секций): {len(docs)}")
    if docs:
        print(docs[0].metadata)
        print(docs[0].page_content[:400])

    save_jsonl(docs, OUT_JSONL)
    print(f"Сохранено: {OUT_JSONL}")