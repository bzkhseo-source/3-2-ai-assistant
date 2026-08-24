from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.models.conversation import ConversationCreate, ConversationListItem, ConversationDetail
from app.services.firestore_service import get_firestore_client

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

COLLECTION_NAME = "conversations"


@router.post("", response_model=ConversationDetail)
def create_conversation(item: ConversationCreate):
    """대화 저장"""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document()

    created_at = datetime.now(timezone.utc).isoformat()
    data = {
        "title": item.title,
        "messages": [m.model_dump() for m in item.messages],
        "created_at": created_at,
    }
    doc_ref.set(data)

    return ConversationDetail(id=doc_ref.id, **data)


@router.get("", response_model=list[ConversationListItem])
def list_conversations():
    """대화 목록 조회 (messages 제외, 요약만)"""
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).order_by(
        "created_at", direction="DESCENDING"
    ).stream()

    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append(ConversationListItem(
            id=doc.id,
            title=data.get("title", "(제목 없음)"),
            message_count=len(data.get("messages", [])),
            created_at=data.get("created_at", ""),
        ))
    return result


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str):
    """특정 대화 상세 조회 (messages 전체 포함) - 대화 불러오기용"""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(conversation_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"대화를 찾을 수 없습니다: {conversation_id}")

    data = doc.to_dict()
    return ConversationDetail(id=doc.id, **data)


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    """대화 삭제"""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(conversation_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"대화를 찾을 수 없습니다: {conversation_id}")

    doc_ref.delete()
    return {"message": "삭제되었습니다.", "id": conversation_id}