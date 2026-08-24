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
> 화면이 바로 로딩되지 않으면 잠시 기다린 후 새로고침해주세요.

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
사용자 질문
→ AI가 필요 여부 판단
→ (필요시) 내부 도구 호출: get_data_summary / get_conversation_history
→ 도구 실행 결과를 AI에게 재전달
→ AI가 최종 자연어 답변 생성


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
http://127.0.0.1:5500/frontend/index.html


### MCP 서버 (선택, 보너스 A 검증용)

```bash
cd mcp_server
python -m venv venv 대신 backend venv 재사용 가능
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
app/services/ai/
base.py # 공통 인터페이스(추상 클래스)
gemini_provider.py # Gemini 구현체
openai_provider.py # OpenAI 구현체
factory.py # .env의 AI_PROVIDER 값을 보고 프로바이더 반환
tools.py # Function Calling용 도구 정의 (프로바이더 독립적)


개발 단계에서는 무료 티어가 넉넉한 Gemini(`gemini-3.5-flash-lite`)를 사용했고,
`.env`의 `AI_PROVIDER` 값만 바꾸면 코드 수정 없이 OpenAI로 전환할 수 있습니다.

### 라우터/서비스 분리
app/
routers/ # API 엔드포인트 (data, conversations, chat)
services/ # 비즈니스 로직 (Firestore 연동, 데이터 요약/통계 계산, AI 호출)
models/ # Pydantic 요청/응답 스키마


## Firebase(Firestore) 설정 상세

- Firestore Database를 사용하며, `data`(시세 데이터), `conversations`(대화 기록) 두 컬렉션으로 구성
- 서비스 계정 인증 방식: Firebase 콘솔에서 발급한 서비스 계정 키(JSON)를 PowerShell로 한 줄 문자열로 압축(`ConvertFrom-Json | ConvertTo-Json -Compress`)하여 `.env`의 `FIREBASE_SERVICE_ACCOUNT_JSON`에 저장, 코드에서 파싱하여 `firebase_admin.initialize_app()`으로 초기화
- 보안 규칙: 개발 단계에서는 테스트 모드로 설정, 실제 서비스에서는 백엔드 API를 통해서만 접근하도록 구성

## 트러블슈팅 기록

| 문제 | 원인 | 해결 |
|---|---|---|
| Firestore 403 오류 (`SERVICE_DISABLED`) | Firestore Database 생성이 실제로는 완료되지 않은 상태였음 (Firebase 콘솔에서 "데이터베이스 만들기"가 미완료) | Firestore 콘솔에서 Database를 다시 정상 생성 |
| venv 혼동으로 명령어 인식 실패 | 여러 프로젝트를 오가며 작업하다 다른 프로젝트의 venv가 활성화된 상태로 명령 실행 | 새 터미널을 열 때마다 활성화된 venv 경로를 확인하는 습관화 |
| Render 배포 실패 (`pywin32` 설치 오류) | Windows 로컬에서 생성한 `requirements.txt`에 Windows 전용 패키지(`pywin32`)가 포함되어 Linux 배포 환경에서 설치 실패 | `requirements.txt`에서 `pywin32==312; sys_platform == 'win32'` 형태로 조건부 설치 명시 |
| MCP 서버 `ModuleNotFoundError: mcp.server.fastmcp` | MCP Python SDK가 2.0으로 업데이트되며 `mcp.server.fastmcp` 모듈이 제거되고 `MCPServer`로 변경됨 | 커뮤니티 표준 독립 패키지 `fastmcp`(PrefectHQ)로 전환, `from fastmcp import FastMCP`로 import 경로만 수정 |
| 배포 사이트 좌측 상단에 의도치 않은 텍스트 노출 | `<head>` 태그 안에 실수로 `<th>` 태그(테이블 헤더용 코드)가 잘못 삽입되어, 브라우저가 이를 `<body>` 시작 지점으로 밀어내며 텍스트만 노출 | 해당 코드를 올바른 위치(`<thead>` 안)로 이동 |

## 제출 스크린샷

- 데이터 요약이 보이는 채팅 화면 (질문+답변 포함): `docs/screenshot-chat.png`
- 데이터 관리 화면 (CRUD 동작 확인): `docs/screenshot-data.png`
- 대화 기록 화면 (불러오기 동작 확인): `docs/screenshot-conversations.png`

## 작성자

서경환 (GN_마리너) — 2026 경남 코디세이(Gyeongnam Codyssey)