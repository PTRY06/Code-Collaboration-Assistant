from __future__ import annotations

import json
import sys
import time
from collections.abc import Generator, Callable

import requests
from src.config import Config

OnToken = Callable[[str], None]

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
RETRYABLE_EXCEPTIONS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
)


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


def _retry_request(
    method: Callable[[], requests.Response],
) -> requests.Response:
    """带指数退避的重试包装器"""
    last_exc: Exception | None = None

    for attempt in range(Config.MAX_RETRIES + 1):
        try:
            resp = method()
            if resp.status_code < 500 or attempt == Config.MAX_RETRIES:
                return resp
            if resp.status_code in RETRYABLE_STATUS:
                raise requests.exceptions.HTTPError(
                    f"{resp.status_code} {resp.reason}",
                    response=resp,
                )
            return resp
        except RETRYABLE_EXCEPTIONS as e:
            last_exc = e
            if attempt < Config.MAX_RETRIES:
                delay = Config.RETRY_BACKOFF_FACTOR ** attempt
                print(
                    f"[LLM] 请求失败 (尝试 {attempt + 1}/{Config.MAX_RETRIES + 1})，"
                    f"{delay:.1f}s 后重试...",
                    file=sys.stderr,
                )
                time.sleep(delay)

    raise last_exc  # type: ignore[misc]


def _handle_request_error(
    e: Exception, response: requests.Response | None = None
) -> None:
    if isinstance(e, requests.exceptions.Timeout):
        print("[LLM] 请求超时", file=sys.stderr)
    elif isinstance(e, requests.exceptions.HTTPError):
        msg = f"[LLM] HTTP 错误: {e}"
        if response is not None:
            try:
                detail = response.json()
                msg += f"\n[LLM] 响应详情: {detail}"
            except Exception:
                pass
        print(msg, file=sys.stderr)
    else:
        print(f"[LLM] 调用失败: {e}", file=sys.stderr)


def call_llm(prompt: str) -> str:
    """非流式调用，返回完整文本"""
    try:
        response = _retry_request(
            lambda: requests.post(
                Config.DEEPSEEK_BASE_URL,
                headers=_build_headers(),
                json=_build_payload(prompt),
                timeout=Config.TIMEOUT,
            )
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        _handle_request_error(e)
        return ""


def call_llm_stream(
    prompt: str,
    on_token: OnToken | None = None,
) -> Generator[str, None, None]:
    yield from call_llm_stream_chat(
        [{"role": "user", "content": prompt}], on_token
    )


def call_llm_stream_chat(
    messages: list[dict],
    on_token: OnToken | None = None,
) -> Generator[str, None, None]:
    payload = _build_chat_payload(messages)
    payload["stream"] = True

    try:
        response = _retry_request(
            lambda: requests.post(
                Config.DEEPSEEK_BASE_URL,
                headers=_build_headers(),
                json=payload,
                timeout=Config.TIMEOUT,
                stream=True,
            )
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

    except Exception as e:
        _handle_request_error(e)
