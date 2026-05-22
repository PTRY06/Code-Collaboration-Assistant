from __future__ import annotations

from collections.abc import Callable

from src.llm_client import call_llm_stream_chat
from src.utils import extract_code_blocks
from src.chat import ChatSession

OnToken = Callable[[str], None]


class WriterAgent:
    """Writer Agent：对话式编程助手，维护多轮对话上下文"""

    @staticmethod
    def chat(
        session: ChatSession,
        user_input: str,
        on_token: OnToken | None = None,
    ) -> str:
        """将用户消息加入会话，流式获取助手回复。
        返回完整的助手回复文本。
        """
        session.add_user(user_input)

        full = "".join(
            call_llm_stream_chat(session.to_api_messages(), on_token=on_token)
        )

        session.add_assistant(full)
        session.last_code_blocks = extract_code_blocks(full)
        return full

    @staticmethod
    def retry_with_error(
        session: ChatSession,
        code: str,
        error_msg: str,
        on_token: OnToken | None = None,
    ) -> str:
        """代码执行失败后，让助手修正并重新生成。"""
        feedback = (
            f"你刚才写的代码运行失败了，请修正它。\n"
            f"\n出错的代码：\n```python\n{code}\n```\n"
            f"\n错误信息：\n{error_msg}\n"
            f"\n请给出修正后的代码，并用 ```python 代码块包裹。"
        )
        session.add_user(feedback)

        full = "".join(
            call_llm_stream_chat(session.to_api_messages(), on_token=on_token)
        )

        session.add_assistant(full)
        session.last_code_blocks = extract_code_blocks(full)
        return full

    @staticmethod
    def comment_on_result(
        session: ChatSession,
        test_output: str,
        on_token: OnToken | None = None,
    ) -> str:
        """代码测试通过后，让助手对结果发表评论。"""
        prompt = (
            f"你的代码刚刚执行完毕，测试结果如下：\n{test_output}\n"
            f"请对这个结果发表简短评论（一两句话即可），确认一切正常。"
        )
        session.add_user(prompt)

        full = "".join(
            call_llm_stream_chat(session.to_api_messages(), on_token=on_token)
        )

        session.add_assistant(full)
        return full
