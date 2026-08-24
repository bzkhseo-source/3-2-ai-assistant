# RESULT — 미션 3-2) AI Agent 개발: 나만의 AI 비서 구축

## 배포 URL

| 구분 | URL |
|---|---|
| 프론트엔드 | https://gn-mission3-2-frontend.vercel.app |
| 백엔드 API | https://gn-mission3-2-ai-assistant.onrender.com |
| Swagger 문서 | https://gn-mission3-2-ai-assistant.onrender.com/docs |
| GitHub 저장소 | https://github.com/bzkhseo-source/3-2-ai-assistant |

> 백엔드는 Render 무료 티어로 배포되어 있어, 미사용 시 슬립 모드로 전환됩니다.
> 첫 요청 시 서버가 깨어나는 데 최대 1분 정도 걸릴 수 있습니다.

## 요약

시계열 데이터(금/은 선물 시세, `GC=F`/`SI=F`, 1년치 502개+)를 분석하여 Firestore에 저장하고,
그 요약 정보를 AI(Gemini)의 시스템 프롬프트에 주입하여 사용자의 실제 데이터를 근거로 답변하는
"내 상황을 아는 AI 비서" 웹 서비스를 구축했습니다.

## 최종 요구사항 이행 현황

| 구분 | 항목 | 상태 |
|---|---|---|
| 필수 | 데이터 기반 AI 채팅 (컨텍스트 주입) | ✅ 완료 |
| 필수 | 데이터 관리 CRUD | ✅ 완료 |
| 필수 | 대화 기록 저장 및 불러오기 | ✅ 완료 |
| 필수 | 백엔드 배포(Render) + Swagger | ✅ 완료 |
| 필수 | 프론트엔드 배포(Vercel) + README | ✅ 완료 |
| 필수 | .env / .gitignore / .env.example 보안 구성 | ✅ 완료 |
| 보너스 A | Function Calling + MCP Server 외부 채널 연동 | ✅ 완료 |
| 보너스 B | 통계 확장 / 시각화 / 내보내기 / 다크모드 | ✅ 완료 |
| 추가 구현 | USD/KRW 통화 전환, 기간 필터, 야후 파이낸스 최신 시세 동기화 | ✅ 완료 |

## 아키텍처 핵심

- **AI 프로바이더 추상화**: `AI_PROVIDER` 환경변수 값으로 Gemini ↔ OpenAI를 코드 수정 없이 런타임 전환 (전략 패턴)
- **라우터/서비스/모델 3계층 분리**: `app/routers`, `app/services`, `app/models`
- **컨텍스트 주입 흐름**: `/api/data/summary` 조회 → 시스템 프롬프트 삽입 → Gemini 호출 → `conversations`에 자동 저장
- **Function Calling**: AI가 필요 시 `get_data_summary`, `get_conversation_history` 도구를 스스로 호출
- **MCP Server**: 기존 FastAPI 엔드포인트를 그대로 감싸는 방식으로, 로직 중복 없이 외부 채널(MCP Inspector로 검증) 지원

## 트러블슈팅 요약

| 문제 | 해결 |
|---|---|
| Firestore 403 (SERVICE_DISABLED) | Firestore Database를 콘솔에서 다시 정상 생성 |
| Render 배포 실패 (pywin32) | `requirements.txt`에 `pywin32==312; sys_platform == 'win32'` 조건부 설치 |
| MCP `ModuleNotFoundError` | MCP SDK 2.0의 breaking change로, 독립 패키지 `fastmcp`로 전환 |
| 배포 사이트 좌측 상단 텍스트 노출 | `<head>`에 잘못 삽입된 `<th>` 태그를 올바른 위치로 이동 |
| `sync-latest` 405 오류 | 변경된 백엔드 코드를 커밋/푸시하여 Render 재배포 |

## 제출 스크린샷

- `docs/screenshot-chat.png` — 데이터 요약이 반영된 채팅 화면 (질문+답변)
- `docs/screenshot-data.png` — 데이터 관리 화면 (CRUD 및 야후 파이낸스 동기화 동작)
- `docs/screenshot-conversations.png` — 대화 기록 목록 및 불러오기 동작

## 상세 내용

전체 미션 개요, 트러블슈팅 원인 분석, 코드 구조, 학습 성과 등 상세 내용은
`나만의_AI_비서_구축_최종_제출_보고서.docx`를 참고하십시오.
