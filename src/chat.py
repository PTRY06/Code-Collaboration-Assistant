"""对话会话管理"""

from __future__ import annotations

from dataclasses import dataclass, field

SYSTEM_PROMPT = (
    "你是 CodeCollab，一个友好的 AI 编程伙伴。你可以用中文或英文与用户交流。\n"
    "\n"
    "你的风格：\n"
    "- 像朋友一样自然对话，解释你的思路和做法\n"
    "- 遇到模糊需求时，主动询问澄清\n"
    "- 在写代码前，用一两句话说明你的方案\n"
    "- 代码放在 ```python ... ``` 代码块中\n"
    "- 代码中包含 if __name__ == '__main__': 测试块，打印输入和输出\n"
    "- 代码执行后你会看到测试结果，可以对结果发表评论\n"
    "\n"
    "不要做的事：\n"
    "- 不要只输出代码不说话\n"
    "- 不要用「你」「用户」第三人称称呼用户，用「你」直接交流\n"
    "- 不要在代码块外写代码"
)


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str

    def to_api(self) -> dict:
        return {"role": self.role, "content": self.content}


class ChatSession:
    """管理多轮对话历史"""

    def __init__(self) -> None:
        self.messages: list[ChatMessage] = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
        ]
        self.last_code_blocks: list[str] = []

    def add_user(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))

    def add_assistant(self, content: str) -> None:
        self.messages.append(ChatMessage(role="assistant", content=content))

    def add_system(self, content: str) -> None:
        self.messages.append(ChatMessage(role="system", content=content))

    def to_api_messages(self) -> list[dict]:
        return [m.to_api() for m in self.messages]

    def history_summary(self) -> str:
        lines = []
        for m in self.messages:
            if m.role == "system" and "你是 CodeCollab" in m.content:
                continue  # skip system prompt in summary
            role_label = {"user": "你", "assistant": "CodeCollab", "system": "[系统]"}.get(m.role, m.role)
            preview = m.content[:80].replace("\n", " ")
            lines.append(f"  {role_label}: {preview}")
        return "\n".join(lines) if lines else "（空对话）"

    def clear(self) -> None:
        self.messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)]
        self.last_code_blocks = []
