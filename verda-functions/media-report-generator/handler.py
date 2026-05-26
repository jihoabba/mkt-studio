"""
Media Report Generator - Verda Function
기간 지정 → CSV fetch → Claude 분석 → HTML 보고서 생성 → VOS 저장
"""
import json
import os
from datetime import datetime
import requests
import boto3
from anthropic import Anthropic

# Google Sheets CSV URLs
PAID_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSj2Av7YPQL4lu2S2B50gZoDWKu1peFqPRQoaLDJr2ydtcPEgB_QYVOQtFOM-2Jpyl0Ws_XF2sd2MhU/pub?gid=1434908615&single=true&output=csv'
OWNED_CONTENT_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT8Scx8b8cCv4mhL_6Xslwu17hIq3J4BstEw2SxPQg6pY3H70dTuf_gVAh07HU9xDzD9DjBagf4v67M/pub?gid=1275250485&single=true&output=csv'
OWNED_FOLLOWER_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT8Scx8b8cCv4mhL_6Xslwu17hIq3J4BstEw2SxPQg6pY3H70dTuf_gVAh07HU9xDzD9DjBagf4v67M/pub?gid=790666469&single=true&output=csv'

def handler(event, context):
    """
    event body = {
        "startMonth": "24년 06월",
        "endMonth": "25년 05월"
    }
    """
    try:
        # 1. 요청 파싱
        body = json.loads(event.get('body', '{}'))
        start_month = body.get('startMonth', '')
        end_month = body.get('endMonth', '')

        if not start_month or not end_month:
            return error_response(400, 'startMonth and endMonth required')

        # 2. CSV 데이터 fetch & 필터링
        paid_summary = fetch_and_filter_paid(start_month, end_month)
        owned_summary = fetch_and_filter_owned(start_month, end_month)

        # 3. Claude API로 보고서 생성
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not anthropic_key:
            return error_response(500, 'ANTHROPIC_API_KEY not configured')

        client = Anthropic(api_key=anthropic_key)
        report_html = generate_report_with_claude(
            client,
            start_month,
            end_month,
            paid_summary,
            owned_summary
        )

        # 4. VOS에 저장
        vos_key = os.environ.get('VOS_ACCESS_KEY')
        vos_secret = os.environ.get('VOS_SECRET_KEY')

        if not vos_key or not vos_secret:
            # VOS 설정 없으면 HTML을 응답으로 반환
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html; charset=utf-8'},
                'body': report_html
            }

        report_url = save_to_vos(
            report_html,
            start_month,
            end_month,
            vos_key,
            vos_secret
        )

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'reportUrl': report_url,
                'period': f'{start_month} ~ {end_month}'
            })
        }

    except Exception as e:
        return error_response(500, str(e))


def fetch_and_filter_paid(start_month, end_month):
    """PAID 데이터 fetch 후 기간 필터링 & 요약"""
    resp = requests.get(PAID_CSV_URL, timeout=30)
    lines = resp.text.strip().split('\n')

    # CSV 파싱 (간단 버전)
    headers = lines[0].split(',')
    rows = []
    for line in lines[1:]:
        cells = line.split(',')
        if len(cells) >= len(headers):
            row = dict(zip(headers, cells))
            # 월 필터링 (간단 비교)
            month_col = row.get('기간', '').strip() or row.get('월', '').strip()
            if start_month <= month_col <= end_month:
                rows.append(row)

    # 집계
    total_cost = sum(float(r.get('광고비', 0) or 0) for r in rows)
    total_revenue = sum(float(r.get('매출', 0) or 0) for r in rows)
    total_purchases = sum(float(r.get('구매 수', 0) or r.get('구매수', 0) or 0) for r in rows)
    roas = (total_revenue / total_cost * 100) if total_cost > 0 else 0

    return {
        'period': f'{start_month} ~ {end_month}',
        'rows_count': len(rows),
        'total_cost': int(total_cost),
        'total_revenue': int(total_revenue),
        'total_purchases': int(total_purchases),
        'roas': round(roas, 1)
    }


def fetch_and_filter_owned(start_month, end_month):
    """OWNED 데이터 fetch 후 기간 필터링 & 요약"""
    resp = requests.get(OWNED_CONTENT_URL, timeout=30)
    lines = resp.text.strip().split('\n')

    headers = lines[0].split(',')
    rows = []
    for line in lines[1:]:
        cells = line.split(',')
        if len(cells) >= len(headers):
            row = dict(zip(headers, cells))
            # 날짜 필터링 (간단 버전)
            date_str = row.get('일시', '').strip()
            # 2024-06 형태로 변환해서 비교
            if date_str and len(date_str) >= 7:
                # YYYY-MM 추출
                ym = date_str[:7].replace('-', '년 ').replace('-', '월') + '월'
                if start_month <= ym <= end_month:
                    rows.append(row)

    total_impressions = sum(int(r.get('노출', 0) or 0) for r in rows)
    total_likes = sum(int(r.get('좋아요', 0) or 0) for r in rows)

    return {
        'period': f'{start_month} ~ {end_month}',
        'posts_count': len(rows),
        'total_impressions': total_impressions,
        'total_likes': total_likes,
        'avg_engagement': round(total_likes / total_impressions * 100, 2) if total_impressions > 0 else 0
    }


def generate_report_with_claude(client, start_month, end_month, paid, owned):
    """Claude API로 보고서 HTML 생성"""

    prompt = f"""당신은 LINE FRIENDS SQUARE 마케팅 애널리스트입니다.
아래 데이터를 분석해서 **경영진 보고용 HTML 리포트**를 작성하세요.

## 분석 기간
{start_month} ~ {end_month}

## PAID MEDIA 데이터
- 총 광고비: {paid['total_cost']:,}원
- 총 매출: {paid['total_revenue']:,}원
- ROAS: {paid['roas']}%
- 구매 수: {paid['total_purchases']:,}건

## OWNED MEDIA 데이터
- 게시물 수: {owned['posts_count']}개
- 총 노출: {owned['total_impressions']:,}회
- 평균 참여율: {owned['avg_engagement']}%

## 요구사항
1. **핵심 인사이트 3가지** (데이터 기반 해석)
2. **ROAS 및 참여율 추이 분석**
3. **다음 기간 권장사항** (구체적인 액션 아이템)

## 출력 형식
- **완전한 HTML 문서** (<!DOCTYPE html>부터 시작)
- Apple Keynote 스타일 디자인 (깔끔, 미니멀)
- Pretendard 폰트 사용
- 모바일 반응형
- 다크모드 지원 불필요
- 색상: LINE FRIENDS 브랜드 컬러 (#00B900 green, #FF6B6B red 등)

**중요**: 설명 없이 HTML 코드만 출력하세요."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def save_to_vos(html_content, start_month, end_month, access_key, secret_key):
    """VOS (S3 호환)에 HTML 저장"""

    s3 = boto3.client(
        's3',
        endpoint_url='https://line-objects-internal.com',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # 버킷명 (환경변수 or 기본값)
    bucket_name = os.environ.get('VOS_BUCKET', 'mkt-studio-reports')

    # 파일명: reports/2024-06_2025-05.html
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    key = f"reports/{start_month.replace('년 ', '-').replace('월', '')}_{end_month.replace('년 ', '-').replace('월', '')}_{timestamp}.html"

    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=html_content.encode('utf-8'),
        ContentType='text/html; charset=utf-8',
        ACL='public-read'  # 공개 읽기 (필요시 수정)
    )

    # 공개 URL 반환
    return f"https://line-objects.com/{bucket_name}/{key}"


def error_response(status_code, message):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': message})
    }
