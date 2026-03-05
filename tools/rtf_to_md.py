#!/usr/bin/env python3
r"""Simple RTF -> Markdown converter tuned for the provided mindmap.

Usage:
    python tools/rtf_to_md.py plan/Goal\ Tactics.rtf

It detects RTF paragraph blocks, reads left-indents like \li400/\li600/...,
maps distinct indent values to nesting levels and emits a bullet list.
"""
import re
import sys
from pathlib import Path


def clean_rtf_text(s: str) -> str:
    # remove unicode escapes like \u8364? and hex escapes \'xx
    s = re.sub(r"\\u-?\d+\??", "", s)
    s = re.sub(r"\\'[0-9a-fA-F]{2}", "", s)
    # remove control words like \fs24, \b0, \par, etc.
    s = re.sub(r"\\[a-zA-Z]+-?\d*\s?", "", s)
    # remove leftover braces
    s = s.replace('{', '').replace('}', '')
    # collapse whitespace
    s = re.sub(r"\s+", ' ', s)
    return s.strip()


def normalize_leading_d(text: str) -> str:
    # remove a stray leading 'd' that appears frequently in this RTF export
    # only when it's the first character and is followed by a letter or digit
    text = re.sub(r"^d(?=[A-Za-z0-9])", "", text)
    # drop solitary 'd' paragraphs
    if text.strip() == 'd':
        return ''
    return text


def rtf_to_md(inpath: Path, outpath: Path):
    raw = inpath.read_text(encoding='utf-8', errors='replace')
    # split into paragraphs by \par control
    parts = re.split(r"\\par", raw)

    items = []
    li_values = []
    for p in parts:
        # skip empty-ish parts
        if not p.strip():
            continue
        # find last \liNNN in the paragraph (if any)
        m = re.findall(r"\\li(\d+)", p)
        li = int(m[-1]) if m else None
        # remove common RTF noise and get plain text
        text = clean_rtf_text(p)
        text = normalize_leading_d(text)
        # sometimes the paragraph contains only control words; skip
        if not text:
            continue
        items.append((li, text))
        if li is not None:
            li_values.append(li)

    # map unique li values to levels (smallest -> 0)
    uniq = sorted(set(li_values))
    mapping = {v: i for i, v in enumerate(uniq)} if uniq else {}

    lines = []
    for li, text in items:
        level = mapping.get(li, 0) if li is not None else 0
        indent = '  ' * level
        lines.append(f"{indent}- {text}")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main(argv):
    if len(argv) < 2:
        print('Usage: rtf_to_md.py <input.rtf> [output.md]')
        return 2
    inpath = Path(argv[1])
    outpath = Path(argv[2]) if len(argv) > 2 else inpath.with_suffix('.md')
    if not inpath.exists():
        print('Input file not found:', inpath)
        return 2
    rtf_to_md(inpath, outpath)
    print('Wrote', outpath)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
