# mkt-studio — 프로젝트 설정

## 위키 접속 정보

- **URL**: https://wiki.workers-hub.com
- **인증 토큰 위치**: Mac 키체인 서비스 `confluence-api-token`
- **사용법**: 
  ```bash
  security find-generic-password -a "$USER" -s confluence-api-token -w
  ```
