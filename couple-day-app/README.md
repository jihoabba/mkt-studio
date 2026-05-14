# 부부의 날 캐릭터상 매칭 · MVP

LINE FRIENDS SQUARE · AX TF · 2026 부부의 날 이벤트 웹앱

## 뭐 하는 앱?

부부 두 사람의 사진을 업로드하면 → 각자에게 어울리는 **캐릭터상**과 → 매칭된 굿즈 + 자동 20% 할인 안내를 보여줍니다.

> 내부 분류 기준은 동물상이지만, **출력은 캐릭터상**(예: "COOKY상", "코니상")으로 우회 표기합니다. IP 회사 컨벤션 준수.

## 어떻게 실행?

```bash
# 1. 단순히 열기 (데모 모드만 동작)
open /Users/user/couple-day-app/index.html

# 2. 로컬 서버로 띄우기 (진짜 분석 모드까지 동작)
cd /Users/user/couple-day-app
python3 -m http.server 8000
# → http://localhost:8000
```

## 두 가지 모드

| 모드 | 동작 | 용도 |
|---|---|---|
| **데모 모드** | API 키 없이 랜덤 매칭 | 디자인·플로우 미리보기 |
| **진짜 분석** | Anthropic Claude Vision 호출 | 실제 동물상 분석 |

진짜 분석 모드에서는 화면 하단에 API 키 입력란이 나타납니다. 키는 `sessionStorage`에만 저장되고 페이지를 닫으면 사라집니다.

> ⚠️ **MVP 한정**: 브라우저에서 직접 Anthropic API를 호출(키 노출 가능)합니다. 실서비스 배포 시 반드시 백엔드(서버리스 함수 등)로 분리해야 합니다.

## 캐릭터 풀

8종 (라인프렌즈 + BT21 혼합)

- **브라운상** · soft & solid
- **코니상** · playful & bright
- **샐리상** · tiny & adorable
- **제임스상** · sleek & charming
- **초코상** · sweet & soft-spoken
- **COOKY상** · cheeky & bold
- **CHIMMY상** · sunny & loyal
- **KOYA상** · calm & thoughtful

내부 동물상 → 캐릭터상 매핑은 `ANIMAL_TO_CHARACTER` 상수 참고.

## 실서비스 연동 시 TODO

- [ ] 온라인팀에서 **실제 할인 대상 SKU 리스트** 받기 (캐릭터별 분류 권장)
- [ ] `PRODUCTS` 상수에 진짜 상품명·가격·이미지 URL 넣기
- [ ] 캐릭터별 Shopify **컬렉션** 만들기
- [ ] Shopify에서 **자동할인 1개** 생성:
  - 타입: BxGy 또는 Basic
  - 조건: "할인 대상 컬렉션"에서 **2개 이상** 담기
  - 혜택: 20% off
  - 기간: 5/21 한정
- [ ] "두 굿즈 함께 담기" 버튼 → Shopify cart permalink (`/cart/add?id=variantId1&id=variantId2`) 또는 Storefront API 연동
- [ ] API 호출을 백엔드로 옮기기 (Vercel Function / Cloudflare Workers)
- [ ] 결과 카드 이미지 다운로드/SNS 공유 기능

## 일정

- 오늘: 2026-05-12
- 부부의 날: 2026-05-21 (D-9)
- 크리티컬 패스: **온라인팀에서 SKU 리스트 받기**
