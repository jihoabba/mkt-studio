# mkt-studio

LINE FRIENDS SQUARE 마케팅 업무 산출물 허브 + 사이드 트랙 통합 워크스페이스.

> 🌐 사내 배포: 사내 정적 배포 서비스 (LandPress 등)에 그대로 업로드
> 🐙 GitHub: https://github.com/jihoabba/mkt-studio
> 🏢 사내 깃: https://git.linecorp.com/yeom/mkt-studio (자동 미러)

---

## 📁 디렉토리 구조

```
mkt-studio/
├── index.html                    ← 메인 허브 (카테고리 · 필터 · 검색)
├── README.md                     ← 이 문서
│
├── reports/                      ← 1-pager 분석 보고서
├── meeting-notes/                ← 회의록 (Apple 스타일 HTML)
├── ideas/                        ← 아이디어 메모 (MD/HTML)
│
├── tools/                        ← 운영 도구
│   ├── data-card/                · 주간 리포트 카드 생성기
│   ├── ig-dashboard/             · 인스타 성과 대시보드
│   └── settlement-check/         · 광고비 정산 체크 (Python)
│
├── prototypes/                   ← 프로토타입 · 이벤트 페이지
│   ├── couple-day-app/           · 부부의 날 캐릭터상 매칭
│   ├── offline-game/             · 오프라인 키오스크 게임
│   ├── popup-manager/            · 팝업 운영 가이드 + 게임
│   ├── fan-square/               · 팬덤 인터랙티브
│   ├── truz-preorder/            · TRUZ 프리오더 랜딩
│   └── mkt-monthly/              · 초기 먼슬리 허브 (legacy)
│
├── projects/                     ← 진행 중 프로젝트
│   ├── youtube-contents/         · YouTube 콘텐츠 (팟캐스트 검토)
│   └── monthly/                  · 월간 보고
│       └── 2026-05/              · ement YTD + 보완 분석 + 슬라이드
│
├── scripts/
│   └── build-manifest.py         ← 메타 블록 스캔 → manifest.json 생성
│
└── _meta/
    └── manifest.json             ← 전체 산출물 인덱스 (index.html이 읽음)
```

---

## 🏷 메타데이터 표준 (RAG 인덱싱용)

**모든 신규 HTML / MD 파일** 상단에 다음 메타 블록을 추가:

### HTML
```html
<!DOCTYPE html>
<!-- ── 문서 메타
  type:  "report" | "meeting" | "idea" | "tool" | "prototype" | "project"
  id:    "YYYY-MM-DD-slug" (또는 unique-slug)
  title: "한 줄 제목"
  desc:  "1~2문장 요약. 핵심 키워드 포함."
  file:  "상대경로/파일명.html"
  date:  "YYYY-MM-DD"
  tags:  ["tag1", "tag2", "tag3"]
── -->
<html lang="ko">
...
```

### Markdown
파일 최상단 (h1 위)에 같은 HTML 주석 블록 삽입.

### 메타 추가 후 — manifest 재빌드
```bash
python3 scripts/build-manifest.py
```
→ `_meta/manifest.json` 갱신 → `index.html`에 자동 반영

---

## 🧑‍💻 신규 산출물 추가 워크플로우

1. **카테고리 선택** — 위 디렉토리 구조 참고
2. **파일명 규칙** — `YYYY-MM-DD-slug.html` (날짜 기반) 또는 `kebab-case.html` (도구·프로토타입)
3. **메타 블록 추가** (상단 표준 참고)
4. **`python3 scripts/build-manifest.py` 실행**
5. **커밋 → 푸시** — `git push` 한 번이면 GitHub + 사내 깃 둘 다 자동 업데이트

---

## 🔍 RAG 활용

`_meta/manifest.json` 은 사내 RAG 인덱서가 그대로 소비 가능한 형식입니다.

```json
{
  "generated_at": "2026-05-22T...",
  "count": 14,
  "items": [
    {
      "type": "report",
      "id": "2026-05-22-ad-efficiency-diagnosis",
      "title": "...",
      "desc": "...",
      "file": "projects/monthly/2026-05/보완_4월-이후....md",
      "date": "2026-05-22",
      "tags": ["report", "monthly", ...]
    },
    ...
  ]
}
```

각 항목의 `file` 경로를 따라가서 본문(HTML/MD) 전체를 함께 임베딩하면 검색·QA 응답이 가능합니다.

---

## 🚀 사내 배포

- 정적 사이트 (모든 파일이 client-side) → 사내 정적 호스팅에 폴더 통째로 업로드
- `index.html` 이 자동으로 `_meta/manifest.json` 을 fetch
- 신규 산출물 푸시 → 배포 → 즉시 반영

---

## 🤖 에이전트 활용

이 폴더는 마케팅 업무 서포트 에이전트의 지식 베이스 역할도 합니다.

- **회의록 검색**: "지난 5월 팀 공유 미팅에서 BT21 관련 이슈 뭐였지?"
- **보고서 참조**: "4월 이후 광고 효율 하락 분석 보여줘"
- **도구 추천**: "주간 리포트 카드뉴스로 만들고 싶어"

→ 에이전트가 `manifest.json` 으로 1차 필터링 → 본문 파싱으로 응답.

---

## 📜 운영 원칙

- **한 산출물 = 한 카테고리** — 중복 배치 금지
- **메타 블록 필수** — 없으면 인덱싱 안 됨 → 허브에 안 보임
- **날짜는 ISO** — `YYYY-MM-DD` 통일 (`26년 5월` 같은 표기 ❌)
- **파일명은 영문 kebab-case 권장** — 검색·URL 편의
- **데이터 컬렉션은 `_meta/` 또는 자체 `data/` 폴더로** — 산출물 폴더 오염 방지
