# merge_book.py
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent / "progit2-ru"
OUTPUT_FILE = BASE_DIR.parent / "pro_git_ru.txt"

include_re = re.compile(r'^\s*include::([^\[]+)\[.*\]\s*$')

def expand_includes(text: str, current_file: Path, seen: set[Path]) -> str:
    out_lines = []
    for line in text.splitlines():
        m = include_re.match(line)
        if not m:
            out_lines.append(line)
            continue

        rel = m.group(1).strip()
        target = (current_file.parent / rel).resolve()

        alt = (REPO_DIR / rel).resolve()

        if target.exists():
            inc_path = target
        elif alt.exists():
            inc_path = alt
        else:
            out_lines.append(f"\n[include-not-found: {rel}]\n")
            continue

        if inc_path in seen:
            # защита от циклов
            out_lines.append(f"\n[include-skipped-cycle: {rel}]\n")
            continue

        seen.add(inc_path)
        inc_text = inc_path.read_text(encoding="utf-8")
        out_lines.append(f"\n\n----- {inc_path.relative_to(REPO_DIR)} -----\n\n")
        out_lines.append(expand_includes(inc_text, inc_path, seen))
    return "\n".join(out_lines)

chapter_skeletons = sorted(REPO_DIR.glob("ch*.asc"))

print(f"Репозиторий: {REPO_DIR}")
print(f"Найдено глав-скелетов: {len(chapter_skeletons)}")

seen_files: set[Path] = set()
with OUTPUT_FILE.open("w", encoding="utf-8") as out:
    for ch in chapter_skeletons:
        out.write(f"\n\n===== {ch.name} =====\n\n")
        seen_files.add(ch.resolve())
        out.write(expand_includes(ch.read_text(encoding="utf-8"), ch, seen_files))

print(f"Готово: {OUTPUT_FILE}")
print(f"Уникальных подключённых файлов: {len(seen_files)}")