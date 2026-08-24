from pydantic import BaseModel, Field, field_validator
import re

# 제어문자(널바이트, 탭/개행 제외) 제거용 패턴
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="사용자 질문 (최대 2000자)",
        examples=["이번 달 실적이 어때?"],
    )
    conversation_id: str | None = Field(
        default=None,
        max_length=100,
        description="이어서 대화할 기존 conversation id (없으면 새 대화 시작)",
    )
    use_tools: bool = Field(default=False, description="True면 AI가 필요시 내부 도구를 스스로 호출")

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        v = _CONTROL_CHAR_PATTERN.sub("", v).strip()
        if not v:
            raise ValueError("메시지에 공백 외의 내용이 없습니다.")
        return v

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        # Firestore 문서 ID는 영문/숫자로 구성되므로 그 외 문자는 조작 시도로 간주해 거부
        if not re.fullmatch(r"[A-Za-z0-9_-]+", v):
            raise ValueError("conversation_id 형식이 올바르지 않습니다.")
        return v


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str