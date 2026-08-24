# RESULT — 미션 3-2) AI Agent 개발: 나만의 AI 비서 구축

## 배포 URL

| 구분 | URL |
|---|---|
| 프론트엔드 | https://gn-mission3-2-frontend.vercel.app |
| 백엔드 API | https://gn-mission3-2-ai-assistant.onrender.com |
| Swagger 문서 | https://gn-mission3-2-ai-assistant.onrender.com/docs |
| GitHub 저장소 | https://github.com/bzkhseo-source/3-2-ai-assistant |

> 백엔드는 Render 무료 티어로 배포되어 있어, 미사용 시 슬립 모드로 전환됩니다.
> 첫 요청 시 서버가 깨어나는 데 최대 1분 정도 걸릴 수 있습니다. 배포 상태는
> [Render 대시보드](https://dashboard.render.com)에서 별도로 확인 가능합니다.

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

## 서비스 계층 책임 (Service Layer Contracts)

| 서비스 함수 | 책임 | 입력 | 출력 |
|---|---|---|---|
| `firestore_service.get_firestore_client()` | Firestore 클라이언트 싱글톤 초기화/반환 | 없음 | Firestore client 객체 |
| `data_service.calculate_summary(records)` | 기간/개수/평균·최대·최소/추세/금은비율 계산 | `list[dict]` — `{date, value, memo}` | `dict` — `{period, count, metrics, trend, ratio}` |
| `data_service.calculate_statistics(records)` | 표준편차, 변동성(%), 최근 7일 변화율 계산 | `list[dict]` | `dict` — memo별 통계 |
| `ai.factory.get_ai_provider()` | `AI_PROVIDER` 값에 따라 Gemini/OpenAI 프로바이더 반환 | 없음 | `AIProvider` 구현체 |
| `ai.base.AIProvider.chat()` / `.chat_with_tools()` | 시스템 프롬프트+기록+메시지로 AI 응답 생성 | `system_prompt, user_message, history` | `str` |

## 컨텍스트 주입의 한계와 완화 방안

| 한계 | 완화 방안 |
|---|---|
| 데이터 누적 시 프롬프트 비대화 우려 | 원본 레코드가 아닌 계산된 통계 요약만 주입 — 레코드 수 무관하게 요약 크기 고정 |
| 요약 시점과 조회 시점의 시차 | 매 `/api/chat` 요청마다 요약 재계산(캐시 없음), 필요 시 `use_tools=true`로 AI가 직접 재조회 |
| 시스템 프롬프트가 외부 AI 서버로 전송됨 | 개인 식별 정보가 아닌 시세 데이터만 다뤄 리스크 낮음 (민감정보 마스킹은 향후 과제) |
| 요약 dict를 문자열 포매팅에 직접 사용 | 각 필드에 기본값 제공(`"정보 없음"` 등)으로 빈 데이터에도 예외 없이 동작 |
| 요약에 없는 세부 질문에 추측 답변 가능성 | Function Calling으로 AI가 필요 시 최신 데이터를 직접 조회하도록 유도 |

## 운영 참고사항

- **저장 실패 처리**: 실패 시 `alert()`로 즉시 알림, 자동 재시도는 미구현 (수동 재시도 가능)
- **동시성**: Firestore의 last-write-wins 동작을 그대로 따름 (별도 트랜잭션 처리 없음)
- **기간 필터 vs 전체 요약**: "데이터 요약" 카드는 항상 전체 기간 기준, 차트/테이블의 기간 필터는 화면 표시 범위만 조정 (서버 요약 계산에는 영향 없음)
- **CORS**: `ALLOWED_ORIGINS`에 로컬 개발 주소와 실제 배포 도메인만 등록, 와일드카드 미사용
- **비밀 관리**: Render/Vercel 환경변수 기능을 그대로 사용 (별도 비밀 관리 서비스는 미도입)

## 알려진 제한사항

- 스크린리더 등 정식 접근성(a11y) 감사 도구를 이용한 검증은 아직 진행하지 않음 (모바일 반응형 화면은 실기기로 확인 완료)
- 네트워크 오류 시 자동 재시도 로직 없음
- `memo` 필드는 서버에서 "금"/"은"으로 제한하지 않음 (UI에서만 제한, API 직접 호출 시 임의 값 입력 가능)
- 특정 기간만의 서버 통계 API(`/api/data/summary?start=&end=`)는 미구현

## 트러블슈팅 요약

| 문제 | 해결 |
|---|---|
| Firestore 403 (SERVICE_DISABLED) | Firestore Database를 콘솔에서 다시 정상 생성 |
| Render 배포 실패 (pywin32) | `requirements.txt`에 `pywin32==312; sys_platform == 'win32'` 조건부 설치 |
| MCP `ModuleNotFoundError` | MCP SDK 2.0의 breaking change로, 독립 패키지 `fastmcp`로 전환 |
| 배포 사이트 좌측 상단 텍스트 노출 | `<head>`에 잘못 삽입된 `<th>` 태그를 올바른 위치로 이동 |
| `sync-latest` 405 오류 | 변경된 백엔드 코드를 커밋/푸시하여 Render 재배포 |

## 제출 스크린샷

| 파일 | 내용 |
|---|---|
| `docs/screenshot-chat.png` | 데이터 요약이 반영된 채팅 화면 (질문+답변) |
| `docs/screenshot-data.png` | 데이터 관리 화면 (CRUD + 야후 파이낸스 동기화) |
| `docs/screenshot-conversations.png` | 대화 기록 목록 및 불러오기 동작 |
| `docs/screenshot-swagger.png` | 배포된 백엔드 Swagger UI (`/docs`) |
| `docs/screenshot-desktop-full.png` | 데스크톱 전체 화면 (요약/차트/기간필터/채팅/대화기록/데이터관리) |
| `docs/mobile/mobile-*.png` | 모바일(iPhone) 반응형 화면 5종 (요약, 차트, 채팅, 대화기록, 데이터관리) |

## 상세 내용

전체 미션 개요, 트러블슈팅 원인 분석, 코드 구조, 학습 성과 등 상세 내용은
`나만의_AI_비서_구축_최종_제출_보고서.docx`를 참고하십시오.
