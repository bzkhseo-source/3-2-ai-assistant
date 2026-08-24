"""
AI가 호출할 수 있는 내부 도구(Function) 정의.
프로바이더 독립적인 형태로 정의하고, 각 프로바이더가 자신의 포맷으로 변환해서 사용한다.
"""

# 프로바이더 독립적인 도구 정의 (이름, 설명, 파라미터 스키마)
TOOL_DEFINITIONS = [
    {
        "name": "get_data_summary",
        "description": "저장된 금/은 시세 데이터의 최신 요약 정보(기간, 개수, 평균/최대/최소, 추세, 금은비율)를 다시 조회한다. 사용자가 최신 통계나 요약을 다시 보여달라고 할 때 사용한다.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_conversation_history",
        "description": "과거에 저장된 대화 목록(제목, 메시지 개수, 생성일)을 조회한다. 사용자가 이전 대화나 기록을 물어볼 때 사용한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "가져올 대화 개수 (기본 5개)",
                }
            },
        },
    },
]


def execute_tool(tool_name: str, tool_args: dict) -> dict:
    """실제 도구 실행 - 내부 서비스 함수를 호출한다"""
    from app.services.firestore_service import get_firestore_client
    from app.services.data_service import calculate_summary

    db = get_firestore_client()

    if tool_name == "get_data_summary":
        docs = db.collection("data").stream()
        records = [doc.to_dict() for doc in docs]
        return calculate_summary(records)

    elif tool_name == "get_conversation_history":
        limit = tool_args.get("limit", 5)
        docs = db.collection("conversations").order_by(
            "created_at", direction="DESCENDING"
        ).limit(limit).stream()
        result = []
        for doc in docs:
            data = doc.to_dict()
            result.append({
                "id": doc.id,
                "title": data.get("title", ""),
                "message_count": len(data.get("messages", [])),
                "created_at": data.get("created_at", ""),
            })
        return {"conversations": result}

    else:
        return {"error": f"알 수 없는 도구: {tool_name}"}