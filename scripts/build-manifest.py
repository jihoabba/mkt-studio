#!/usr/bin/env python3
"""
mkt-studio manifest builder.

스캔 대상 폴더의 HTML / MD 파일에서 메타 블록을 파싱해서
_meta/manifest.json 으로 통합.

메타 블록 표준:
  HTML:
    <!-- ── 문서 메타
      type:  "..."
      id:    "..."
      ...
    ── -->

  MD:
    <!-- ── 문서 메타
      ...
    ── -->

사용:
    python3 scripts/build-manifest.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ["reports", "meeting-notes", "ideas", "tools", "prototypes", "projects"]
OUTPUT = ROOT / "_meta" / "manifest.json"

META_RE = re.compile(r"<!--\s*──\s*문서\s*메타(.*?)──\s*-->", re.DOTALL)
KV_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.+?)\s*$", re.MULTILINE)


def parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [s.strip().strip('"') for s in inner.split(",") if s.strip()]
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    return raw


def parse_meta(text: str) -> dict | None:
    m = META_RE.search(text)
    if not m:
        return None
    body = m.group(1)
    out = {}
    for k, v in KV_RE.findall(body):
        out[k] = parse_value(v)
    return out


def scan_file(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    return parse_meta(text)


def main() -> int:
    items = []
    for dirname in SCAN_DIRS:
        d = ROOT / dirname
        if not d.exists():
            continue
        for path in sorted(d.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in (".html", ".md"):
                continue
            meta = scan_file(path)
            if not meta:
                continue
            # Auto-fill file path if missing
            meta.setdefault("file", str(path.relative_to(ROOT)))
            items.append(meta)

    items.sort(key=lambda x: x.get("date", ""), reverse=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "count": len(items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"✓ {len(items)} items → {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
