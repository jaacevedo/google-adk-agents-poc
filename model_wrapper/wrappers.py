from __future__ import annotations

import json
import os
from typing import Any
from typing import AsyncGenerator

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from openai import AsyncAzureOpenAI


def _normalize_json_schema(schema: Any) -> Any:
    """Recursively convert Google GenAI type names (e.g. 'STRING') to
    lowercase JSON Schema equivalents expected by Azure OpenAI ('string')."""
    if isinstance(schema, list):
        return [_normalize_json_schema(item) for item in schema]
    if not isinstance(schema, dict):
        return schema

    result: dict[str, Any] = {}
    for key, value in schema.items():
        if key == "type" and isinstance(value, str):
            result[key] = value.lower()
        elif key in ("properties", "definitions", "$defs") and isinstance(value, dict):
            result[key] = {k: _normalize_json_schema(v) for k, v in value.items()}
        elif key == "items":
            result[key] = _normalize_json_schema(value)
        elif key == "anyOf" or key == "oneOf" or key == "allOf":
            result[key] = [_normalize_json_schema(v) for v in (value or [])]
        else:
            result[key] = value
    return result


def _schema_to_dict(schema: Any) -> dict[str, Any]:
    if schema is None:
        return {}
    if isinstance(schema, dict):
        raw = schema
    elif hasattr(schema, "model_dump"):
        raw = schema.model_dump(exclude_none=True, by_alias=True)
    else:
        return {}
    return _normalize_json_schema(raw)


def _content_to_openai_messages(content: types.Content) -> list[dict[str, Any]]:
    role = "assistant" if content.role == "model" else (content.role or "user")
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    tool_messages: list[dict[str, Any]] = []

    for idx, part in enumerate(content.parts or []):
        if part.function_response:
            response = part.function_response.response
            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": part.function_response.id or f"tool_{idx}",
                    "content": response if isinstance(response, str) else json.dumps(response, ensure_ascii=False),
                }
            )
            continue

        if part.function_call:
            tool_calls.append(
                {
                    "id": part.function_call.id or f"call_{idx}",
                    "type": "function",
                    "function": {
                        "name": part.function_call.name,
                        "arguments": json.dumps(part.function_call.args or {}, ensure_ascii=False),
                    },
                }
            )
            continue

        if part.text:
            text_parts.append(part.text)

    messages: list[dict[str, Any]] = []
    if text_parts or tool_calls:
        msg: dict[str, Any] = {"role": role}
        if text_parts:
            msg["content"] = "\n".join(text_parts)
        if tool_calls and role == "assistant":
            msg["tool_calls"] = tool_calls
            if "content" not in msg:
                msg["content"] = ""
        messages.append(msg)

    messages.extend(tool_messages)
    return messages


def _adk_contents_to_openai_messages(contents: list[types.Content]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for content in contents:
        messages.extend(_content_to_openai_messages(content))
    return messages


def _adk_tools_to_openai_tools(llm_request: LlmRequest) -> list[dict[str, Any]]:
    config = llm_request.config
    if not config or not config.tools:
        return []

    tools: list[dict[str, Any]] = []
    for tool in config.tools:
        function_declarations = getattr(tool, "function_declarations", None)
        if not function_declarations:
            continue

        for declaration in function_declarations:
            if not declaration or not declaration.name:
                continue

            parameters: dict[str, Any] = {"type": "object", "properties": {}}
            if declaration.parameters_json_schema:
                parameters = _normalize_json_schema(declaration.parameters_json_schema)
            elif declaration.parameters and declaration.parameters.properties:
                props: dict[str, Any] = {}
                for key, value in declaration.parameters.properties.items():
                    props[key] = _schema_to_dict(value)
                parameters = {"type": "object", "properties": props}
                required = getattr(declaration.parameters, "required", None)
                if required:
                    parameters["required"] = required
            else:
                # Fallback: serialize the whole parameters object
                raw = _schema_to_dict(declaration.parameters)
                if raw:
                    parameters = raw

            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": declaration.name,
                        "description": declaration.description or "",
                        "parameters": parameters,
                    },
                }
            )

    return tools


class AzureFoundryWrapper(BaseLlm):
    endpoint: str
    api_key: str
    api_version: str
    deployment: str
    client: AsyncAzureOpenAI | None = None

    def __init__(self, model: str | None = None):
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-nano")

        if not endpoint:
            raise ValueError("Falta AZURE_OPENAI_ENDPOINT en variables de entorno.")
        if not api_key:
            raise ValueError("Falta AZURE_OPENAI_KEY en variables de entorno.")

        super().__init__(
            model=model or deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            deployment=deployment,
        )
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        if stream:
            raise NotImplementedError("Streaming no implementado para AzureFoundryWrapper.")

        self._maybe_append_user_content(llm_request)
        messages = _adk_contents_to_openai_messages(llm_request.contents)
        tools = _adk_tools_to_openai_tools(llm_request)

        request_payload: dict[str, Any] = {
            "model": self.deployment,
            "messages": messages,
            "max_completion_tokens": 16384,
        }

        if tools:
            request_payload["tools"] = tools

        if llm_request.config:
            if llm_request.config.max_output_tokens is not None:
                request_payload["max_completion_tokens"] = llm_request.config.max_output_tokens

        response = await self.client.chat.completions.create(**request_payload)
        choice = response.choices[0]
        message = choice.message

        parts: list[types.Part] = []
        if message.content:
            parts.append(types.Part.from_text(text=message.content))

        for tool_call in message.tool_calls or []:
            if not tool_call.function or not tool_call.function.name:
                continue
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            part = types.Part.from_function_call(
                name=tool_call.function.name,
                args=args,
            )
            if tool_call.id:
                part.function_call.id = tool_call.id
            parts.append(part)

        if not parts:
            parts.append(types.Part.from_text(text=""))

        yield LlmResponse(content=types.Content(role="model", parts=parts))
