# 나만의 AI 비서 - 금/은 시세 분석 서비스

시계열 데이터(금·은 선물 시세)를 분석하고, 그 요약 정보를 AI의 시스템 프롬프트에 주입하여
"내 데이터를 아는" 맞춤형 답변을 제공하는 풀스택 웹 서비스입니다.

일반적인 AI 챗봇은 사용자의 데이터를 모르지만, 이 서비스는 Firestore에 저장된 실제 금/은
시세 데이터를 분석해 요약하고, 그 요약을 컨텍스트로 주입해 AI가 실제 수치를 근거로 답변합니다.

## 배포 URL

| 구분 | URL |
|---|---|
| 프론트엔드 | https://gn-mission3-2-frontend.vercel.app |
| 백엔드 API | https://gn-mission3-2-ai-assistant.onrender.com |
| Swagger 문서 | https://gn-mission3-2-ai-assistant.onrender.com/docs |

> ⚠️ 백엔드는 Render 무료 티어로 배포되어 있어, 일정 시간 미사용 시 슬립 모드로 전환됩니다.
> 슬립 상태에서 첫 요청 시 서버가 깨어나는 데 약 30초~1분 정도 지연될 수 있습니다.
> 화면이 바로 로딩되지 않으면 잠시 기다린 후 새로고침해주세요. 배포 상태 자체가 궁금하다면
> [Render 대시보드](https://dashboard.render.com)에서 서비스 상태를 별도로 확인할 수 있습니다.

## 기술 스택

- **백엔드**: FastAPI, Uvicorn, Pydantic
- **데이터베이스**: Firebase Firestore
- **AI**: Google Gemini API (`gemini-3.5-flash-lite`), OpenAI API(제출/전환용) — 프로바이더 추상화 구조로 런타임 전환 가능
- **데이터 수집/분석**: yfinance, pandas
- **프론트엔드**: HTML / CSS / JavaScript (바닐라, 프레임워크 미사용), Canvas API(자체 구현 차트)
- **외부 채널 연동**: MCP Server (fastmcp)
- **배포**: Render(백엔드), Vercel(프론트엔드)

## 주요 기능

1. **데이터 기반 AI 채팅**: 데이터 요약을 시스템 프롬프트에 주입해 맞춤형 답변 제공 (컨텍스트 주입)
2. **데이터 관리(CRUD)**: 금/은 시세 데이터 추가/조회/수정/삭제
3. **대화 기록 저장 및 불러오기**: 대화 목록 조회, 특정 대화 재조회
4. **기간별 조회**: 시작일/종료일을 지정해 차트·데이터 테이블을 특정 구간만 필터링
5. **최신 시세 동기화**: 야후 파이낸스(yfinance)에서 최신 금/은 시세를 수동으로 가져와 반영 (중복 방지 로직 포함)

## 보너스 과제

### A. Function Calling + 멀티채널 연동

- `AIProvider.chat_with_tools()`가 AI에게 `get_data_summary`, `get_conversation_history` 두 가지 내부 도구를 제공합니다.
- AI는 사용자의 질문 의도를 스스로 판단해 필요할 때만 도구를 호출합니다. 예: "최신 데이터 요약을 다시 보여줘" → `get_data_summary` 자동 호출.
- **외부 채널 연동**: `mcp_server/server.py`에 MCP(Model Context Protocol) 서버를 구현했습니다. FastAPI 엔드포인트(`/api/data/summary`, `/api/conversations`, `/api/chat`)를 그대로 감싸는 방식으로, 로직은 FastAPI 한 곳에만 두고 MCP는 외부 클라이언트용 창구 역할만 하도록 설계했습니다. MCP Inspector로 연결 및 도구 호출을 검증했습니다.

**호출 흐름**

```
사용자 질문
  → AI가 필요 여부 판단
  → (필요시) 내부 도구 호출: get_data_summary / get_conversation_history
  → 도구 실행 결과를 AI에게 재전달
  → AI가 최종 자연어 답변 생성
```

**MCP 도구 목록**
- `get_data_summary`: 저장된 금/은 시세 데이터의 요약 정보 조회
- `get_conversation_history`: 과거 저장된 대화 목록 조회
- `ask_ai_assistant`: AI 비서에게 질문하고 데이터 컨텍스트가 반영된 답변 수신

### B. 인사이트·UX 고도화

- **통계 확장**: `GET /api/data/statistics` — 변동성(표준편차), 변동성 비율, 최근 7일 변화율 등 추가 지표 제공
- **시각화**: 프론트엔드에서 Canvas API로 직접 구현한 라인 차트 (외부 차트 라이브러리 미사용)
- **내보내기**: CSV / JSON 다운로드 버튼 제공
- **다크 모드**: 토글 버튼으로 라이트/다크 테마 전환 (localStorage에 저장되어 재방문 시 유지)
- **추가 구현**: USD/KRW 통화 전환(실시간 환율 API 연동, 실패 시 대체 환율로 폴백), 기간별 데이터 조회 필터, 야후 파이낸스 최신 시세 수동 동기화

## 로컬 실행 방법

### 백엔드

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell 기준
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs` 에서 Swagger UI 확인 가능합니다.

### 프론트엔드

`frontend/index.html`을 VSCode의 Live Server 확장으로 열어주세요 (파일을 직접 더블클릭해서 여는 `file://` 방식은 CORS로 인해 데이터 로딩이 되지 않습니다).

```
http://127.0.0.1:5500/frontend/index.html
```

### MCP 서버 (선택, 보너스 A 검증용)

```bash
cd mcp_server
pip install -r requirements.txt
npx @modelcontextprotocol/inspector python server.py
```

## 환경 변수

`backend/.env.example` 참고 (실제 값은 `.env`에 설정, git에는 포함되지 않습니다):

```env
AI_PROVIDER=gemini                 # gemini 또는 openai
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
FIREBASE_SERVICE_ACCOUNT_JSON=     # 서비스 계정 키 JSON을 한 줄로 압축한 문자열
ALLOWED_ORIGINS=http://localhost:5500,https://your-frontend.vercel.app
API_BASE_URL=http://localhost:8000
```

## 아키텍처 설계 포인트

### AI 프로바이더 추상화

`AI_PROVIDER` 환경변수 값에 따라 Gemini/OpenAI 중 원하는 프로바이더를 런타임에 전환할 수 있도록
전략 패턴(Strategy Pattern)으로 설계했습니다.

```
app/services/ai/
  base.py              # 공통 인터페이스(추상 클래스)
  gemini_provider.py   # Gemini 구현체
  openai_provider.py   # OpenAI 구현체
  factory.py           # .env의 AI_PROVIDER 값을 보고 프로바이더 반환
  tools.py             # Function Calling용 도구 정의 (프로바이더 독립적)
```

개발 단계에서는 무료 티어가 넉넉한 Gemini(`gemini-3.5-flash-lite`)를 사용했고,
`.env`의 `AI_PROVIDER` 값만 바꾸면 코드 수정 없이 OpenAI로 전환할 수 있습니다.

### 라우터/서비스 분리

```
app/
  routers/     # API 엔드포인트 (data, conversations, chat)
  services/    # 비즈니스 로직 (Firestore 연동, 데이터 요약/통계 계산, AI 호출)
  models/      # Pydantic 요청/응답 스키마
```

### 서비스 계층 책임 (Service Layer Contracts)

| 서비스 함수 | 책임 | 입력 | 출력 |
|---|---|---|---|
| `firestore_service.get_firestore_client()` | Firestore 클라이언트 싱글톤 초기화/반환 | 없음 (환경변수 `FIREBASE_SERVICE_ACCOUNT_JSON` 참조) | Firestore client 객체 |
| `data_service.calculate_summary(records)` | 원본 레코드 목록을 받아 기간/개수/평균·최대·최소/추세/금은비율을 계산 | `list[dict]` — `{date, value, memo}` | `dict` — `{period, count, metrics, trend, ratio}` |
| `data_service.calculate_statistics(records)` | 표준편차, 변동성(%), 최근 7일 변화율 계산 | `list[dict]` | `dict` — memo별 `{std_dev, volatility_pct, recent_7d_change_pct, latest_value, latest_date}` |
| `ai.factory.get_ai_provider()` | `.env`의 `AI_PROVIDER` 값에 따라 Gemini/OpenAI 프로바이더 인스턴스 반환 | 없음 | `AIProvider` 구현체 |
| `ai.base.AIProvider.chat()` / `.chat_with_tools()` | 시스템 프롬프트+기록+메시지를 받아 AI 응답 문자열 생성 | `system_prompt: str, user_message: str, history: list[dict]` | `str` (AI 응답) |

## 요약 API 입력/출력 예시

**`GET /api/data/summary`** — 입력 파라미터 없음

```json
{
  "period": "2025-08-25 ~ 2026-08-24",
  "count": 508,
  "metrics": {
    "금": { "count": 254, "average": 4373.09, "max": 5318.4, "min": 3373.8 },
    "은": { "count": 254, "average": 65.88, "max": 115.08, "min": 38.58 }
  },
  "trend": { "금": "상승 (약 1.1%)", "은": "하락 (약 -6.6%)" },
  "ratio": { "gold_silver_ratio": 97.3 }
}
```

재사용 시나리오: 위 응답을 그대로 `SYSTEM_PROMPT_TEMPLATE.format(**summary)` 형태로 시스템
프롬프트에 주입하거나, 프론트엔드 요약 카드 렌더링에 그대로 사용합니다.

## 컨텍스트 주입의 한계와 완화 방안

이 서비스의 핵심인 "데이터 요약을 시스템 프롬프트에 주입하는 방식"에는 아래와 같은
구조적 한계가 있으며, 이를 인지하고 아래처럼 완화하고 있습니다.

| 한계 | 설명 | 완화 방안 |
|---|---|---|
| 토큰/컨텍스트 한도 | 데이터가 계속 누적되면 요약 자체가 커져 시스템 프롬프트가 비대해질 수 있음 | 원본 레코드 전체가 아니라 `calculate_summary()`가 계산한 통계 요약(평균/최대/최소/추세 등)만 주입 — 레코드 수가 늘어도 요약 크기는 거의 고정 |
| 요약 시점과 실제 조회 시점의 시차 | 채팅 응답 생성 중 다른 곳에서 데이터가 바뀌면, 그 사이 시점의 요약을 근거로 답변할 수 있음 | 매 `/api/chat` 요청마다 요약을 새로 계산(캐시하지 않음)해 최신 상태를 최대한 반영. 실시간성이 중요한 경우 `use_tools=true`로 `get_data_summary`를 AI가 직접 재조회하도록 유도 가능 |
| 개인정보/민감정보 노출 | 시스템 프롬프트에 들어가는 데이터가 AI 제공사 서버로 전송됨 | 본 서비스는 개인 식별 정보가 아닌 시세 데이터(날짜/가격/구분)만 다루므로 프라이버시 리스크가 낮음. 다만 사용자가 개인 재무 데이터 등 민감한 값을 직접 입력할 경우, 별도 마스킹/필터링 로직은 아직 없어 향후 개선 과제로 남김 |
| 요약 포맷의 일관성 | `calculate_summary()`가 반환하는 dict를 그대로 문자열 포매팅(`.format()`)에 사용하고 있어, 값이 비어있거나 구조가 바뀌면 프롬프트 텍스트가 부자연스러워질 수 있음 | `SYSTEM_PROMPT_TEMPLATE`은 각 필드에 기본값(`"정보 없음"`, `{}` 등)을 제공하여 빈 데이터에도 예외 없이 동작하도록 처리. 향후 dict를 사람이 읽기 좋은 문장으로 직렬화하는 별도 포맷터 도입을 고려 중 |
| AI가 잘못된 근거로 답변할 가능성 | 통계 요약만 주입되므로, 특정 날짜의 세부 값처럼 요약에 없는 질문에는 AI가 추측성 답변을 할 수 있음 | Function Calling(`get_data_summary`, `get_conversation_history`)으로 AI가 필요 시 최신 데이터를 직접 조회하도록 하여 추측 답변 가능성을 낮춤 |

## 데이터 검증 규칙

| 필드 | 서버(Pydantic) 검증 | 클라이언트 검증 |
|---|---|---|
| `date` | `str` 필수 (형식 강제는 하지 않음, `YYYY-MM-DD` 권장) | `<input type="date">`로 형식 강제 |
| `value` | `float` 필수 | `parseFloat` 결과가 `NaN`이면 전송 차단 |
| `memo` | `str` 필수 (자유 문자열이며 "금"/"은"으로 제한하지 않음) | `<select>`로 "금"/"은" 두 값만 선택 가능하도록 UI에서 제한 |
| `message` (채팅) | `str` 필수, 1~2000자, 제어문자 제거 후 공백만 남으면 거부 | 없음 (서버 검증에 의존) |
| `conversation_id` (채팅) | `str` \| `None`, 지정 시 `[A-Za-z0-9_-]+` 정규식만 허용 | 없음 (서버가 발급한 값을 그대로 재사용) |

> 현재는 `memo`에 임의 문자열이 서버로 들어올 수 있는 구조입니다. 요약/통계 계산은
> `groupby(memo)` 방식이라 어떤 문자열이든 그룹으로 처리되지만, 프론트 UI를 우회한 직접
> API 호출 시 "금"/"은" 외의 값이 들어갈 수 있는 점은 알려진 제한사항입니다.

### 채팅 입력 서버측 검증 (2차 보완)

평가 피드백을 반영하여 `POST /api/chat`에 아래 서버측 검증을 추가했다 (`app/models/chat.py`).

- **길이 제한**: `message`는 1~2000자. 초과 시 422로 즉시 거부하여 시스템 프롬프트를 압도하거나 과금을 유발하는 시도를 차단
- **제어문자 제거 + 공백 검증**: 널바이트 등 제어문자를 제거한 뒤 남는 내용이 공백뿐이면 422로 거부
- **`conversation_id` 형식 검증**: Firestore 문서 ID를 그대로 조회에 쓰므로 `[A-Za-z0-9_-]+` 외의 값(예: 경로 순회 시도 `../etc/passwd`)은 422로 차단
- **구조적 방어**: 시스템 프롬프트와 사용자 메시지는 API 레벨에서 서로 다른 필드로 분리 전달되며, Function Calling으로 AI가 실행 가능한 동작은 `get_data_summary`/`get_conversation_history` 두 가지로 고정되어 있어, 프롬프트 인젝션이 일부 성공해도 실질적 피해 범위가 제한적이다.

실제 검증: 2000자 초과 메시지, 공백만 있는 메시지, `conversation_id: "../etc/passwd"` 세 가지 모두 422로 정상 차단되는 것을 배포 환경에서 확인했다.

## 저장 실패 시 처리 정책

- **데이터/대화 저장(POST)**: 요청 실패 시 `alert()`로 사용자에게 즉시 알리고, 폼 입력값은
  초기화하지 않아 재시도가 가능합니다. 별도의 자동 재시도(retry)는 구현하지 않았습니다.
- **원자성**: Firestore의 단일 문서 `set()`/`update()`는 그 자체로 원자적입니다. 다만
  "대화 저장 성공 + summary 계산" 같은 여러 단계를 하나의 트랜잭션으로 묶지는 않았으므로,
  중간 단계에서 실패하면 부분 반영될 수 있습니다. 현재 서비스 규모(개인 프로젝트, 단일 사용자
  중심 데이터)에서는 리스크가 낮다고 판단해 별도 트랜잭션 처리는 적용하지 않았습니다.
- **동시성**: 여러 클라이언트가 동시에 같은 데이터를 수정하는 시나리오는 고려하지 않았습니다
  (Firestore의 last-write-wins 동작을 그대로 따릅니다).

## 기간 필터 우선순위 및 동기화

- **프론트엔드 화면(요약 카드/차트/테이블)**: 기본값은 항상 Firestore에 저장된 **전체 기간** 데이터를 기준으로 표시합니다. 클라이언트 측 기간 필터(`filterStartDate`~`filterEndDate`)는 차트·테이블의 화면 표시 범위만 조정합니다.
- **서버 API 기간 필터 (2차 보완)**: 평가 피드백을 반영하여 `GET /api/data/summary`, `GET /api/data/statistics`에 선택적 쿼리 파라미터 `start`, `end`(`YYYY-MM-DD`)를 추가했습니다. 지정 시 해당 기간의 레코드만 집계하여 반환합니다 (예: `/api/data/summary?start=2026-01-01&end=2026-03-31`). 두 파라미터 모두 생략하면 기존과 동일하게 전체 기간을 반환합니다.
- **현재 프론트엔드 연동 범위**: 프론트엔드는 아직 이 서버측 기간 필터 파라미터를 채팅 컨텍스트 주입(`/api/chat`)에는 연동하지 않았습니다 — `/api/chat`은 여전히 전체 기간 요약을 시스템 프롬프트에 사용합니다. 특정 기간 기준 AI 답변이 필요하다면 향후 `/api/chat`에도 기간 파라미터를 전달하는 확장이 가능합니다.

## Firebase(Firestore) 설정 상세

- Firestore Database를 사용하며, `data`(시세 데이터), `conversations`(대화 기록) 두 컬렉션으로 구성
- 서비스 계정 인증 방식: Firebase 콘솔에서 발급한 서비스 계정 키(JSON)를 PowerShell로 한 줄 문자열로 압축(`ConvertFrom-Json | ConvertTo-Json -Compress`)하여 `.env`의 `FIREBASE_SERVICE_ACCOUNT_JSON`에 저장, 코드에서 파싱하여 `firebase_admin.initialize_app()`으로 초기화
- 보안 규칙: 개발 단계에서는 테스트 모드로 설정, 실제 서비스에서는 백엔드 API를 통해서만 접근하도록 구성

## 배포 및 운영 참고사항

- **배포 상태 확인**: 프론트엔드 또는 백엔드 Swagger가 응답하지 않으면, Render 무료 티어의
  콜드 스타트(최대 약 1분)일 가능성이 높습니다. 잠시 후 새로고침해주세요. Render 대시보드의
  서비스 상태는 `https://dashboard.render.com`에서 확인 가능합니다.
- **콜드 스타트 완화**: 별도의 워밍(ping) 스케줄러는 구현하지 않았습니다. 무료 티어 특성상
  주기적 핑을 걸어도 결국 슬립되므로, 현재는 프론트엔드에서 요청이 느릴 수 있다는 안내 문구로
  대응하고 있습니다(본 문서 상단 안내 참고).
- **CORS 오리진 관리**: `ALLOWED_ORIGINS` 환경변수에는 로컬 개발 주소(`localhost:5500`)와
  실제 배포된 Vercel 도메인만 등록되어 있으며, 와일드카드(`*`)는 사용하지 않습니다.
- **비밀 관리**: 현재는 Render/Vercel의 환경변수 기능을 그대로 사용하고 있으며, 별도의 비밀
  관리 서비스(AWS Secrets Manager 등)는 도입하지 않았습니다. 개인 학습 프로젝트 규모에서는
  플랫폼 제공 환경변수로 충분하다고 판단했으나, 실서비스 확장 시에는 비밀 관리 서비스 도입과
  서비스 계정 키의 최소 권한(least privilege) 설정을 권장합니다.

## 알려진 제한사항 (Known Limitations)

- 모바일 실기기(iPhone, 5G) 반응형 화면을 `docs/mobile/` 폴더에 캡처로 검증했습니다 (요약 카드, 시세 차트, 채팅, 대화 기록, 데이터 관리 5개 화면). 다만 스크린리더 등 정식 접근성(a11y) 감사 도구를 이용한 검증은 아직 진행하지 않았습니다.
- 네트워크 오류 시 자동 재시도 로직은 없으며, 사용자가 버튼을 다시 눌러야 합니다.
- Firestore 쿼리에 별도 복합 인덱스를 설계하지 않았습니다 (현재 쿼리 패턴이 단순하여 자동 인덱스로 충분).
- `memo` 필드는 API 레벨에서 "금"/"은"으로 제한되어 있지 않습니다 (프론트 UI에서만 제한).
- `GET /api/data/summary`, `/statistics`는 서버측 기간 필터(`start`/`end`)를 지원하지만, `POST /api/chat`(AI 컨텍스트 주입)에는 아직 연동하지 않아 항상 전체 기간 기준으로 답변합니다.
- 채팅 메시지에 대한 서버측 길이·형식 검증은 추가했으나, 별도의 콘텐츠 모더레이션(욕설/유해 표현 필터링)은 구현하지 않았습니다.

## 트러블슈팅 기록

| 문제 | 원인 | 해결 |
|---|---|---|
| Firestore 403 오류 (`SERVICE_DISABLED`) | Firestore Database 생성이 실제로는 완료되지 않은 상태였음 (Firebase 콘솔에서 "데이터베이스 만들기"가 미완료) | Firestore 콘솔에서 Database를 다시 정상 생성 |
| venv 혼동으로 명령어 인식 실패 | 여러 프로젝트를 오가며 작업하다 다른 프로젝트의 venv가 활성화된 상태로 명령 실행 | 새 터미널을 열 때마다 활성화된 venv 경로를 확인하는 습관화 |
| Render 배포 실패 (`pywin32` 설치 오류) | Windows 로컬에서 생성한 `requirements.txt`에 Windows 전용 패키지(`pywin32`)가 포함되어 Linux 배포 환경에서 설치 실패 | `requirements.txt`에서 `pywin32==312; sys_platform == 'win32'` 형태로 조건부 설치 명시 |
| MCP 서버 `ModuleNotFoundError: mcp.server.fastmcp` | MCP Python SDK가 2.0으로 업데이트되며 `mcp.server.fastmcp` 모듈이 제거되고 `MCPServer`로 변경됨 | 커뮤니티 표준 독립 패키지 `fastmcp`(PrefectHQ)로 전환, `from fastmcp import FastMCP`로 import 경로만 수정 |
| 배포 사이트 좌측 상단에 의도치 않은 텍스트 노출 | `<head>` 태그 안에 실수로 `<th>` 태그(테이블 헤더용 코드)가 잘못 삽입되어, 브라우저가 이를 `<body>` 시작 지점으로 밀어내며 텍스트만 노출 | 해당 코드를 올바른 위치(`<thead>` 안)로 이동 |
| `POST /api/data/sync-latest` 405 오류 | 배포된 프론트엔드가 이미 Render 백엔드를 바라보고 있었으나, 새로 추가한 엔드포인트 코드가 아직 배포에 반영되지 않음 | 변경된 백엔드 코드를 커밋/푸시하여 Render 재배포 |

## 제출 스크린샷

| 파일 | 내용 |
|---|---|
| `docs/screenshot-chat.png` | 데이터 요약이 반영된 채팅 화면 (질문+답변) |
| `docs/screenshot-data.png` | 데이터 관리 화면 (CRUD + 야후 파이낸스 동기화 동작) |
| `docs/screenshot-conversations.png` | 대화 기록 목록 및 특정 대화 불러오기 동작 |
| `docs/screenshot-swagger.png` | 배포된 백엔드 Swagger UI (`/docs`) |
| `docs/screenshot-desktop-full.png` | 데스크톱 전체 화면 (요약/차트/기간필터/채팅/대화기록/데이터관리 통합) |
| `docs/mobile/mobile-summary.png` | 모바일(iPhone) 데이터 요약 화면 |
| `docs/mobile/mobile-chart.png` | 모바일 시세 추이 차트 화면 |
| `docs/mobile/mobile-chat.png` | 모바일 AI 채팅 화면 |
| `docs/mobile/mobile-conversations.png` | 모바일 대화 기록 화면 |
| `docs/mobile/mobile-data.png` | 모바일 데이터 관리 화면 |

## 작성자

서경환 (GN_마리너) — 2026 경남 코디세이(Gyeongnam Codyssey)
