#!/usr/bin/env python3
"""Package skills/hallmark as an uploadable Skill for Claude chat (claude.ai and the desktop app).

Claude chat only accepts a small set of SKILL.md frontmatter keys, so this rewrites the
frontmatter (moving `version` and `argument-hint` under `metadata`) and leaves out files
that only matter to coding harnesses. Output: dist/hallmark-claude-chat.zip
"""
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "hallmark"
OUT = ROOT / "dist" / "hallmark-claude-chat.zip"
ALLOWED = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
SKIP_PARTS = {"agents", "fixtures", ".DS_Store", "node_modules"}
MAX_BYTES = 30 * 1024 * 1024


def rewrite_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit("SKILL.md has no frontmatter")
    top, meta = [], []
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        key = line.split(":", 1)[0].strip()
        if key == "metadata":
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                meta.append(lines[i])
                i += 1
            continue
        if key in ALLOWED:
            top.append(line)
        else:
            value = line.split(":", 1)[1].strip()
            if not value.startswith('"'):
                value = '"' + value.strip("'") + '"'
            meta.append(f"  {key}: {value}")
        i += 1
    if not any(l.startswith("license:") for l in top):
        top.append("license: MIT")
    fm = "\n".join(top + (["metadata:"] + meta if meta else []))
    # Claude chat rejects anything that looks like an XML tag, e.g. `<path>`.
    fm = re.sub(r"<([^<>]*)>", lambda t: t.group(1).upper(), fm)
    return f"---\n{fm}\n---\n" + text[m.end():]


def main():
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(SKILL.rglob("*")):
            rel = path.relative_to(SKILL)
            if path.is_dir() or SKIP_PARTS & set(rel.parts):
                continue
            arc = f"hallmark/{rel.as_posix()}"
            if rel.as_posix() == "SKILL.md":
                z.writestr(arc, rewrite_frontmatter(path.read_text(encoding="utf-8")))
            else:
                z.write(path, arc)
    size = OUT.stat().st_size
    if size > MAX_BYTES:
        sys.exit(f"{OUT} is {size} bytes, over the upload limit")
    print(f"wrote {OUT.relative_to(ROOT)} ({size / 1048576:.1f} MB)")


if __name__ == "__main__":
    main()
