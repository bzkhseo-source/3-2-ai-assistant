from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.models.chat import ChatRequest, ChatResponse
from app.services.firestore_service import get_firestore_client
from app.services.data_service import calculate_summary
from app.services.ai.factory import get_ai_provider

router = APIRouter(prefix="/api/chat", tags=["chat"])

DATA_COLLECTION = "data"
CONV_COLLECTION = "conversations"

SYSTEM_PROMPT_TEMPLATE = """당신은 데이터 분석 비서입니다.

[사용자 데이터 요약]
- 데이터 기간: {period}
- 총 레코드: {count}개
- 주요 지표: {metrics}
- 최근 트렌드: {trend}
- 금/은 비율: {ratio}

위 데이터를 기반으로 맞춤형 답변을 제공하세요. 숫자는 자연스러운 문장으로 풀어서 설명하세요."""


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    db = get_firestore_client()

    # 1. 데이터 요약 조회
    docs = db.collection(DATA_COLLECTION).stream()
    records = [doc.to_dict() for doc in docs]
    summary = calculate_summary(records)

    # 2. 요약을 시스템 프롬프트에 삽입
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        period=summary.get("period", "정보 없음"),
        count=summary.get("count", 0),
        metrics=summary.get("metrics", {}),
        trend=summary.get("trend", {}),
        ratio=summary.get("ratio", {}),
    )

    # 3. 기존 대화 불러오기 (이어서 대화하는 경우)
    history: list[dict] = []
    conversation_id = request.conversation_id
    existing_title = None

    if conversation_id:
        doc_ref = db.collection(CONV_COLLECTION).document(conversation_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"대화를 찾을 수 없습니다: {conversation_id}")
        data = doc.to_dict()
        history = data.get("messages", [])
        existing_title = data.get("title")

    # 4. GPT(Gemini) API 호출
    try:
        ai = get_ai_provider()
        if request.use_tools:
            reply = ai.chat_with_tools(system_prompt, request.message, history)
        else:
            reply = ai.chat(system_prompt, request.message, history)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 응답 생성 실패: {str(e)}")

    # 5. 대화 내용을 conversations에 자동 저장
    new_messages = history + [
        {"role": "user", "content": request.message},
        {"role": "assistant", "content": reply},
    ]

    if conversation_id:
        db.collection(CONV_COLLECTION).document(conversation_id).update({
            "messages": new_messages
        })
    else:
        title = existing_title or request.message[:30]
        doc_ref = db.collection(CONV_COLLECTION).document()
        doc_ref.set({
            "title": title,
            "messages": new_messages,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        conversation_id = doc_ref.id

    return ChatResponse(reply=reply, conversation_id=conversation_id)