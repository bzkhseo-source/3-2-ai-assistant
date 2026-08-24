"""
GN Codyssey 미션 3-2: 나만의 AI 비서 - MCP Server

이 MCP 서버는 로컬에서 실행 중인 FastAPI 백엔드(http://127.0.0.1:8000)를 감싸서
Claude Desktop 등 MCP 클라이언트가 우리 서비스의 데이터 요약/대화 기능을
"도구"로 호출할 수 있게 한다.
"""

import httpx
from fastmcp import FastMCP

API_BASE_URL = "http://127.0.0.1:8000"

mcp = FastMCP("gn-mission3-2-assistant")


@mcp.tool()
def get_data_summary() -> dict:
    """저장된 금/은 시세 데이터의 요약 정보(기간, 개수, 평균/최대/최소, 추세, 금은비율)를 조회한다."""
    response = httpx.get(f"{API_BASE_URL}/api/data/summary", timeout=10.0)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_conversation_history(limit: int = 5) -> dict:
    """과거 저장된 대화 목록(제목, 메시지 개수, 생성일)을 조회한다."""
    response = httpx.get(f"{API_BASE_URL}/api/conversations", timeout=10.0)
    response.raise_for_status()
    conversations = response.json()
    return {"conversations": conversations[:limit]}


@mcp.tool()
def ask_ai_assistant(message: str) -> dict:
    """나만의 AI 비서에게 질문하고, 데이터 컨텍스트가 반영된 답변을 받는다."""
    response = httpx.post(
        f"{API_BASE_URL}/api/chat",
        json={"message": message, "use_tools": False},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run(transport="stdio")