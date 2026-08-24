from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 질문", examples=["이번 달 실적이 어때?"])
    conversation_id: str | None = Field(default=None, description="이어서 대화할 기존 conversation id")
    use_tools: bool = Field(default=False, description="True면 AI가 필요시 내부 도구를 스스로 호출")

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str