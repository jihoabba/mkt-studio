# Media Report Generator - Verda Function

LINE FRIENDS SQUARE 마케팅 데이터를 Claude API로 분석해서 HTML 보고서 생성

## 구조

```
handler.py          # 메인 로직
requirements.txt    # 패키지 의존성
__init__.py         # Python 패키지
```

## 동작 흐름

1. **HTTP POST 요청** → `/analyze`
2. **CSV Fetch** → Google Sheets (PAID + OWNED)
3. **기간 필터링** → startMonth ~ endMonth
4. **Claude API** → 데이터 분석 + HTML 생성
5. **VOS 저장** → S3 호환 오브젝트 스토리지
6. **URL 반환** → 생성된 보고서 링크

## Verda Console 배포

### 1. Function 생성

- **Name**: `media-report-generator`
- **Runtime**: Python 3.x
- **Trigger**: HTTP
- **Timeout**: 120초 (Claude API 응답 대기)

### 2. 환경변수 설정

```
ANTHROPIC_API_KEY=sk-ant-api03-...
VOS_ACCESS_KEY=your-vos-access-key
VOS_SECRET_KEY=your-vos-secret-key
VOS_BUCKET=mkt-studio-reports
```

### 3. 코드 업로드

Option A: **GitHub Source Base**
- Git repo: `git.linecorp.com/yeom/mkt-studio`
- Path: `verda-functions/media-report-generator/`

Option B: **Inline (Template)**
- Copy `handler.py` content
- Add `requirements.txt` dependencies

## 테스트 요청

```bash
curl -X POST https://your-function-url.verda.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "startMonth": "24년 06월",
    "endMonth": "25년 05월"
  }'
```

## 응답 예시

**성공 (VOS 저장):**
```json
{
  "success": true,
  "reportUrl": "https://line-objects.com/mkt-studio-reports/reports/24-06_25-05_20260526-143022.html",
  "period": "24년 06월 ~ 25년 05월"
}
```

**성공 (VOS 미설정 시 HTML 직접 반환):**
```html
<!DOCTYPE html>
<html>...보고서 HTML...</html>
```

## 다음 단계

1. Verda Console에서 Function 생성
2. 환경변수 입력 (ANTHROPIC_API_KEY 필수)
3. VOS 버킷 생성 (`mkt-studio-reports`)
4. media-dashboard.html에 "보고서 생성" 버튼 추가
