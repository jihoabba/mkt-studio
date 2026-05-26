import json
import os
import requests
from anthropic import Anthropic

PAID_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSj2Av7YPQL4lu2S2B50gZoDWKu1peFqPRQoaLDJr2ydtcPEgB_QYVOQtFOM-2Jpyl0Ws_XF2sd2MhU/pub?gid=1434908615&single=true&output=csv'
OWNED_CONTENT_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT8Scx8b8cCv4mhL_6Xslwu17hIq3J4BstEw2SxPQg6pY3H70dTuf_gVAh07HU9xDzD9DjBagf4v67M/pub?gid=1275250485&single=true&output=csv'

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        start = body.get('startMonth', '')
        end = body.get('endMonth', '')
        if not start or not end:
            return {'statusCode': 400, 'body': json.dumps({'error': 'missing months'})}
        paid = fetch_paid(start, end)
        owned = fetch_owned(start, end)
        key = os.environ.get('ANTHROPIC_API_KEY')
        if not key:
            return {'statusCode': 500, 'body': json.dumps({'error': 'no API key'})}
        client = Anthropic(api_key=key)
        html = generate_report(client, start, end, paid, owned)
        return {'statusCode': 200, 'headers': {'Content-Type': 'text/html'}, 'body': html}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

def fetch_paid(start, end):
    resp = requests.get(PAID_CSV_URL, timeout=30)
    lines = resp.text.strip().split('\n')
    headers = lines[0].split(',')
    rows = []
    for line in lines[1:]:
        cells = line.split(',')
        if len(cells) >= len(headers):
            row = dict(zip(headers, cells))
            m = row.get('월', '').strip()
            if start <= m <= end:
                rows.append(row)
    cost = sum(float(r.get('광고비', 0) or 0) for r in rows)
    revenue = sum(float(r.get('매출', 0) or 0) for r in rows)
    purchases = sum(float(r.get('구매수', 0) or 0) for r in rows)
    return {'cost': int(cost), 'revenue': int(revenue), 'purchases': int(purchases), 'roas': round(revenue/cost*100, 1) if cost > 0 else 0}

def fetch_owned(start, end):
    resp = requests.get(OWNED_CONTENT_URL, timeout=30)
    lines = resp.text.strip().split('\n')
    headers = lines[0].split(',')
    rows = []
    for line in lines[1:]:
        cells = line.split(',')
        if len(cells) >= len(headers):
            rows.append(dict(zip(headers, cells)))
    impressions = sum(int(r.get('노출', 0) or 0) for r in rows)
    likes = sum(int(r.get('좋아요', 0) or 0) for r in rows)
    return {'posts': len(rows), 'impressions': impressions, 'likes': likes, 'engagement': round(likes/impressions*100, 2) if impressions > 0 else 0}

def generate_report(client, start, end, paid, owned):
    prompt = f"""LINE FRIENDS SQUARE 마케팅 보고서 HTML 작성.

기간: {start} ~ {end}

PAID: 광고비 {paid['cost']:,}원, 매출 {paid['revenue']:,}원, ROAS {paid['roas']}%, 구매 {paid['purchases']:,}건
OWNED: 게시물 {owned['posts']}개, 노출 {owned['impressions']:,}회, 참여율 {owned['engagement']}%

요구: 1) 인사이트 3개 2) ROAS/참여율 분석 3) 권장사항

완전한 HTML 문서. 코드만."""
    message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=4096, messages=[{"role": "user", "content": prompt}])
    return message.content[0].text
