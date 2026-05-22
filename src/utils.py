from __future__ import annotations

import re


def extract_code(text: str) -> str:
    """从 LLM 返回的文本中提取 Python 代码块"""
    text = text.strip()

    markers = ["```python", "```py", "```"]
    for marker in markers:
        if marker in text:
            start = text.find(marker) + len(marker)
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()

    return text


def extract_code_blocks(text: str) -> list[str]:
    """提取文本中所有 Python 代码块，返回列表"""
    blocks: list[str] = []
    pattern = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)
    for match in pattern.finditer(text):
        blocks.append(match.group(1).strip())
    return blocks


def has_code_block(text: str) -> bool:
    """检查文本是否包含代码块"""
    return bool(re.search(r"```(?:python|py)?[^`]*```", text))
