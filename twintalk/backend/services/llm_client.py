"""LLM Client — unified interface to call OpenAI-compatible APIs."""

import json
import logging
import os
import re
from typing import Generator, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

_client: Optional[OpenAI] = None


def _get_api_key() -> str:
    """Return a validated API key for the configured OpenAI-compatible provider."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    invalid_values = {
        "",
        "your-hunyuan-api-key-here",
        "sk-your-api-key-here",
    }
    if api_key in invalid_values:
        raise RuntimeError(
            "OPENAI_API_KEY 未配置。请在 backend/.env 中填写腾讯混元控制台生成的 API Key，而不是示例占位符。"
        )

    if api_key.startswith("AKID"):
        raise RuntimeError(
            "当前 OPENAI_API_KEY 看起来是腾讯云 SecretId。OpenAI 兼容接口需要使用混元控制台生成的 API Key，而不是 SecretId/SecretKey。"
        )

    return api_key


def get_client() -> OpenAI:
    """Get or create the OpenAI client singleton."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=_get_api_key(),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
    return _client


def get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _extract_json_object(content: str) -> Optional[dict]:
    """Best-effort extraction for providers that do not support response_format."""
    if not content:
        return None

    text = content.strip()
    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced_match:
        text = fenced_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            data, _ = decoder.raw_decode(text[index:])
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue

    return None


def call_llm(
    system_prompt: str,
    user_message: str,
    history: list = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Call the LLM and return the full response text."""
    client = get_client()
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


def call_llm_stream(
    system_prompt: str,
    user_message: str,
    history: list = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> Generator[str, None, None]:
    """Call the LLM and yield response chunks (SSE)."""
    client = get_client()
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        stream = client.chat.completions.create(
            model=get_model(),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"LLM stream call failed: {e}")
        raise


def call_llm_json(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4000,
) -> Optional[dict]:
    """Call the LLM expecting a JSON response. Returns parsed dict or None."""
    client = get_client()
    messages = [
        {
            "role": "system",
            "content": "你是一个结构化数据生成助手。请严格按照要求输出 JSON 格式，不要包含任何其他文本。",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        try:
            response = client.chat.completions.create(
                model=get_model(),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            logger.warning(
                "Structured JSON response_format unavailable for model %s, falling back to text parsing: %s",
                get_model(),
                exc,
            )
            fallback_messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一个结构化数据生成助手。"
                        "请只输出一个合法 JSON 对象，不要输出 Markdown、解释、前后缀文本。"
                    ),
                },
                {"role": "user", "content": prompt},
            ]
            response = client.chat.completions.create(
                model=get_model(),
                messages=fallback_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        content = response.choices[0].message.content or ""
        parsed = _extract_json_object(content)
        if parsed is None:
            logger.error("Failed to extract JSON object from LLM response: %s", content)
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        return None
    except Exception as e:
        logger.error(f"LLM JSON call failed: {e}")
        return None
