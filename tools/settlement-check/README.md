<!-- ── 문서 메타
  type:  "tool"
  id:    "settlement-check"
  title: "광고비 정산 체크 도구"
  desc:  "검수확인서.xlsx + 정산 RAW.xlsx 파싱 → 매체별 비용 합산·오차 검증 → 발주서 PDF 변환 → _체크시트.html 자동 생성. AppleScript 기반 macOS 전용."
  file:  "tools/settlement-check/README.md"
  date:  "2026-04-15"
  tags:  ["tool", "settlement", "ad-budget", "automation", "python", "macos"]
── -->

# 광고비 정산 체크 도구

월별 광고비 정산 검수를 자동화하는 macOS용 Python 스크립트.

## 사용법
```bash
python3 tools/settlement-check/settlement_check.py                   # 최신 폴더 자동 선택
python3 tools/settlement-check/settlement_check.py "<폴더경로>"      # 특정 폴더 지정
python3 tools/settlement-check/settlement_check.py --no-pdf          # PDF 변환 건너뛰기
python3 tools/settlement-check/settlement_check.py --tolerance 0.1   # 허용 오차 (기본 10%)
```

## 흐름
1. **검수확인서.xlsx 파싱** — 예산별 금액 표 + 총합 추출
2. **정산 RAW.xlsx 비교** — 매체 시트 비용 합산해서 ±오차 검증
3. **검수확인서 + 발주서 → PDF 변환** (AppleScript / Word·Excel 호출)
4. **_체크시트.html 생성** — 결과를 브라우저에서 자동으로 열림

## 의존성
- Python 3.x
- `openpyxl`
- macOS (AppleScript 사용)

## 원래 위치
`/Users/user/AX-TF/tools/settlement_check.py` 에서 이관 (2026-05-22).
