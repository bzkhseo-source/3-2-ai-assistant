from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routers import data as data_router
from app.routers import conversations as conversations_router
from app.routers import chat as chat_router

load_dotenv()

app = FastAPI(
    title="나만의 AI 비서 - 금/은 시세 분석 서비스",
    description="시계열 데이터(금/은 시세)를 분석하고 AI가 컨텍스트를 반영해 답변하는 API",
    version="1.0.0"
)

# CORS 설정 - 환경변수로 허용 도메인 관리
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(data_router.router)
app.include_router(conversations_router.router)
app.include_router(chat_router.router)

@app.get("/")
def root():
    return {"message": "AI Assistant API is running", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.services.firestore_service import get_firestore_client


@app.get("/health/firestore")
def health_check_firestore():
    try:
        db = get_firestore_client()
        # 연결 테스트용: 컬렉션 목록 조회 시도
        collections = [c.id for c in db.collections()]
        return {"status": "connected", "collections": collections}
    except Exception as e:
        return {"status": "error", "detail": str(e)}