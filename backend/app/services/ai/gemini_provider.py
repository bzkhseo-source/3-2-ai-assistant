import os
from google import genai
from google.genai import types
from app.services.ai.base import AIProvider
from app.services.ai.tools import TOOL_DEFINITIONS, execute_tool


def _to_gemini_tools() -> list[types.Tool]:
    """중립 도구 정의를 Gemini SDK가 요구하는 FunctionDeclaration 형태로 변환"""
    declarations = []
    for tool in TOOL_DEFINITIONS:
        declarations.append(
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=tool["parameters"],
            )
        )
    return [types.Tool(function_declarations=declarations)]


class GeminiProvider(AIProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def _build_contents(self, history: list[dict], user_message: str) -> list[types.Content]:
        contents = []
        for msg in history:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))
        return contents

    def chat(self, system_prompt: str, user_message: str, history: list[dict]) -> str:
        contents = self._build_contents(history, user_message)
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=1024,
            ),
        )
        return response.text

    def chat_with_tools(self, system_prompt: str, user_message: str, history: list[dict]) -> str:
        contents = self._build_contents(history, user_message)
        tools = _to_gemini_tools()

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=tools,
                max_output_tokens=1024,
            ),
        )

        candidate = response.candidates[0]
        function_call_part = None
        for part in candidate.content.parts:
            if part.function_call:
                function_call_part = part.function_call
                break

        # AI가 도구 호출을 요청하지 않았다면, 그냥 텍스트 답변 반환
        if function_call_part is None:
            return response.text

        # AI가 도구 호출을 요청한 경우: 실제로 실행하고, 결과를 다시 AI에게 전달
        tool_name = function_call_part.name
        tool_args = dict(function_call_part.args) if function_call_part.args else {}
        tool_result = execute_tool(tool_name, tool_args)

        contents.append(candidate.content)  # AI의 함수 호출 요청 메시지 추가
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": tool_result},
                    )
                ],
            )
        )

        final_response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=tools,
                max_output_tokens=1024,
            ),
        )
        return final_response.text