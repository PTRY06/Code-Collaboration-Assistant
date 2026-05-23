from __future__ import annotations

import re


def extract_code_blocks(text: str) -> list[str]:
    """提取文本中所有 Python 代码块，返回列表"""
    blocks: list[str] = []
    pattern = re.compile(r"```(?:python|py)?[ \t]*\n?(.*?)```", re.DOTALL)
    for match in pattern.finditer(text):
        blocks.append(match.group(1).strip())
    return blocks
