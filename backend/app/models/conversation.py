from pydantic import BaseModel, Field
from typing import Literal


class Message(BaseModel):
    """대화 메시지 하나"""
    role: Literal["user", "assistant"] = Field(..., description="발화자 (user 또는 assistant)")
    content: str = Field(..., description="메시지 내용")


class ConversationCreate(BaseModel):
    """대화 저장 요청 스키마"""
    title: str = Field(..., description="대화 제목 (예: 첫 메시지 요약)", examples=["이번 달 실적 문의"])
    messages: list[Message] = Field(..., description="전체 메시지 목록")


class ConversationListItem(BaseModel):
    """대화 목록 조회 시 반환되는 요약 정보 (messages 미포함)"""
    id: str
    title: str
    message_count: int
    created_at: str


class ConversationDetail(BaseModel):
    """대화 상세 조회 시 반환 (messages 포함)"""
    id: str
    title: str
    messages: list[Message]
    created_at: str