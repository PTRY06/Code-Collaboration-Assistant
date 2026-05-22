from __future__ import annotations

import json
import sys
from collections.abc import Generator, Callable

import requests
from src.config import Config

OnToken = Callable[[str], None]


def _build_headers() -> dict:
    return {
        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }


def _build_payload(prompt: str) -> dict:
    return {
        "model": Config.DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": Config.TEMPERATURE,
    }


def _build_chat_payload(messages: list[dict]) -> dict:
    return {
        "model": Config.DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": Config.TEMPERATURE,
    }


def call_llm(prompt: str) -> str:
    """非流式调用，返回完整文本"""
    try:
        response = requests.post(
            Config.DEEPSEEK_BASE_URL,
            headers=_build_headers(),
            json=_build_payload(prompt),
            timeout=Config.TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        print("[LLM] 请求超时", file=sys.stderr)
        return ""
    except requests.exceptions.HTTPError as e:
        print(f"[LLM] HTTP 错误: {e}", file=sys.stderr)
        try:
            detail = response.json()
            print(f"[LLM] 响应详情: {detail}", file=sys.stderr)
        except Exception:
            pass
        return ""
    except Exception as e:
        print(f"[LLM] 调用失败: {e}", file=sys.stderr)
        return ""


def call_llm_stream(
    prompt: str,
    on_token: OnToken | None = None,
) -> Generator[str, None, None]:
    """流式调用，兼容旧版单条 prompt 接口"""
    yield from call_llm_stream_chat(
        [{"role": "user", "content": prompt}], on_token
    )


def call_llm_stream_chat(
    messages: list[dict],
    on_token: OnToken | None = None,
) -> Generator[str, None, None]:
    """流式调用 DeepSeek API，支持多轮对话消息列表。
    每收到一个 token 就调用 on_token 回调，同时 yield 该 token。
    """
    payload = _build_chat_payload(messages)
    payload["stream"] = True

    try:
        response = requests.post(
            Config.DEEPSEEK_BASE_URL,
            headers=_build_headers(),
            json=payload,
            timeout=Config.TIMEOUT,
            stream=True,
        )
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            line = line.strip()
            if not line.startswith("data: "):
                continue

            data_str = line[6:]
            if data_str == "[DONE]":
                break

            try:
                chunk = json.loads(data_str)
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    if on_token:
                        on_token(content)
                    yield content
            except (json.JSONDecodeError, IndexError, KeyError):
                continue

    except requests.exceptions.Timeout:
        print("[LLM] 请求超时", file=sys.stderr)
    except requests.exceptions.HTTPError as e:
        print(f"[LLM] HTTP 错误: {e}", file=sys.stderr)
        try:
            detail = response.json()
            print(f"[LLM] 响应详情: {detail}", file=sys.stderr)
        except Exception:
            pass
    except Exception as e:
        print(f"[LLM] 调用失败: {e}", file=sys.stderr)
