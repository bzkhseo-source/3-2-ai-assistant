from pydantic import BaseModel, Field
from typing import Optional


class DataCreate(BaseModel):
    """데이터 추가 요청 스키마"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)", examples=["2026-08-24"])
    value: float = Field(..., description="시세 값(종가)", examples=[4674.8])
    memo: str = Field(..., description="구분 태그 (예: 금, 은)", examples=["금"])


class DataUpdate(BaseModel):
    """데이터 수정 요청 스키마 - 부분 수정 허용"""
    date: Optional[str] = None
    value: Optional[float] = None
    memo: Optional[str] = None


class DataResponse(BaseModel):
    """데이터 응답 스키마"""
    id: str
    date: str
    value: float
    memo: str