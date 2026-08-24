from abc import ABC, abstractmethod


class AIProvider(ABC):
    """모든 AI 프로바이더(Gemini, OpenAI 등)가 구현해야 하는 공통 인터페이스"""

    @abstractmethod
    def chat(self, system_prompt: str, user_message: str, history: list[dict]) -> str:
        """도구 호출 없이 단순 대화만 하는 경우"""
        raise NotImplementedError

    @abstractmethod
    def chat_with_tools(self, system_prompt: str, user_message: str, history: list[dict]) -> str:
        """
        AI가 필요하다고 판단하면 내부 도구(Function)를 스스로 호출하고,
        그 결과를 반영해서 최종 답변을 생성한다.
        """
        raise NotImplementedError