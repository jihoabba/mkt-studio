#!/usr/bin/env python3
"""
manifest.json 의 모든 MD 항목을 동일 위치의 .html로 변환.

- 메타 블록(<!-- ── 문서 메타 ── -->) 보존
- title을 메타에서 추출해 <title>에 반영
- Pretendard 폰트 + 깔끔한 문서 스타일

사용:
    python3 scripts/render-md.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "_meta" / "manifest.json"

META_RE = re.compile(r"<!--\s*──\s*문서\s*메타(.*?)──\s*-->", re.DOTALL)
KV_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.+?)\s*$", re.MULTILINE)


def parse_meta(text: str) -> dict:
    m = META_RE.search(text)
    if not m:
        return {}
    out = {}
    for k, v in KV_RE.findall(m.group(1)):
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        out[k] = v
    return out


def strip_meta(text: str) -> str:
    return META_RE.sub("", text, count=1).lstrip()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg: #ffffff;
  --surface: #f9fafb;
  --text: #1d1d1f;
  --text-secondary: rgba(0,0,0,0.62);
  --text-muted: rgba(0,0,0,0.45);
  --accent: #0071e3;
  --divider: rgba(0,0,0,0.08);
  --code-bg: #f5f5f7;
}}
html, body {{
  background: var(--bg);
  font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", sans-serif;
  color: var(--text);
  -webkit-font-smoothing: antialiased;
  font-size: 16px;
  line-height: 1.7;
  letter-spacing: -0.005em;
}}
.topbar {{
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--divider);
  position: sticky; top: 0; z-index: 100;
  height: 52px;
  display: flex; align-items: center;
  padding: 0 24px;
  gap: 12px;
}}
.topbar a {{ font-size: 13px; font-weight: 600; color: var(--accent); text-decoration: none; }}
.topbar .sep {{ width: 1px; height: 14px; background: var(--divider); }}
.topbar .title {{ font-size: 13px; font-weight: 500; color: var(--text-secondary); }}
main {{
  max-width: 740px;
  margin: 0 auto;
  padding: 48px 32px 80px;
}}
h1 {{ font-size: 32px; font-weight: 800; letter-spacing: -0.025em; line-height: 1.2; margin: 0 0 14px; }}
h2 {{ font-size: 22px; font-weight: 700; letter-spacing: -0.015em; margin: 36px 0 12px; padding-top: 10px; }}
h3 {{ font-size: 17px; font-weight: 700; margin: 24px 0 10px; }}
h4 {{ font-size: 15px; font-weight: 700; margin: 20px 0 8px; color: var(--text-secondary); }}
p {{ margin: 0 0 14px; color: var(--text-secondary); }}
strong {{ color: var(--text); font-weight: 700; }}
em {{ font-style: italic; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
ul, ol {{ margin: 0 0 16px 24px; }}
li {{ margin-bottom: 6px; color: var(--text-secondary); }}
li > p {{ margin-bottom: 8px; }}
blockquote {{
  border-left: 3px solid var(--accent);
  padding: 8px 18px;
  margin: 14px 0 18px;
  background: var(--surface);
  color: var(--text-secondary);
  border-radius: 0 8px 8px 0;
}}
blockquote p {{ margin: 0; }}
code {{
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 13px;
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  color: #b95000;
}}
pre {{
  background: var(--code-bg);
  border: 1px solid var(--divider);
  border-radius: 10px;
  padding: 16px 18px;
  overflow-x: auto;
  margin: 0 0 18px;
}}
pre code {{ background: none; padding: 0; color: var(--text); font-size: 12.5px; }}
hr {{ border: none; border-top: 1px solid var(--divider); margin: 32px 0; }}
table {{
  border-collapse: collapse;
  width: 100%;
  margin: 0 0 18px;
  font-size: 14px;
}}
th, td {{
  text-align: left;
  padding: 10px 14px;
  border-bottom: 1px solid var(--divider);
}}
th {{ background: var(--surface); font-weight: 700; color: var(--text); font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; }}
td {{ color: var(--text-secondary); }}
td strong {{ color: var(--text); }}
img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0; }}
.muted {{ color: var(--text-muted); font-size: 13px; }}
</style>
</head>
<body>
<nav class="topbar">
  <a href="../../../index.html">← 허브로</a>
  <span class="sep"></span>
  <span class="title">{title}</span>
</nav>
<main>
{content}
</main>
</body>
</html>
"""


def to_relative_topbar(out_path: Path) -> str:
    """root까지 거슬러가는 ../ 횟수 계산."""
    rel = out_path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return "../" * depth if depth > 0 else "./"


def render_md_file(md_path: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    meta = parse_meta(text)
    body = strip_meta(text)
    title = meta.get("title", md_path.stem)

    html_body = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])

    out_path = md_path.with_suffix(".html")
    depth_path = to_relative_topbar(out_path)
    html = HTML_TEMPLATE.replace("../../../index.html", depth_path + "index.html")
    html = html.format(title=title, content=html_body)

    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> int:
    if not MANIFEST.exists():
        print("✗ manifest.json 없음. scripts/build-manifest.py 먼저 실행", file=sys.stderr)
        return 1

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    count = 0
    for item in data.get("items", []):
        file_path = item.get("file", "")
        if not file_path.endswith(".md"):
            continue
        md_path = ROOT / file_path
        if not md_path.exists():
            print(f"  - SKIP (없음): {file_path}")
            continue
        out = render_md_file(md_path)
        print(f"  ✓ {file_path} → {out.relative_to(ROOT)}")
        count += 1

    print(f"\n{count} 파일 변환 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
