"""共享编排器 — Writer-Tester 闭环的单一实现，供 CLI 和 Shell 共用"""

from __future__ import annotations

import sys
from collections.abc import Callable

from src.chat import ChatSession
from src.config import Config
from src.agents.writer import WriterAgent
from src.agents.tester import TesterAgent

OnToken = Callable[[str], None]
OnStatus = Callable[[str], None]


def run_writer_tester(
    user_input: str,
    chat: ChatSession | None = None,
    on_token: OnToken | None = None,
    on_status: OnStatus | None = None,
    quiet: bool = False,
) -> tuple[bool, list[str], int]:
    """执行一次完整的 Writer-Tester 闭环。

    参数:
        user_input: 用户需求
        chat: 可选，复用已有的 ChatSession；为 None 则新建
        on_token: 流式输出回调
        on_status: 状态消息回调（用于 UI 层显示 [Tester] 等）
        quiet: 静默模式，抑制流式输出

    返回:
        (成功, 最终代码块列表, 迭代次数)
    """
    if chat is None:
        chat = ChatSession()

    def _status(msg: str) -> None:
        if on_status:
            on_status(msg)
        elif not quiet:
            print(msg)

    def _token(t: str) -> None:
        if on_token:
            on_token(t)
        elif not quiet:
            sys.stdout.write(t)
            sys.stdout.flush()

    # 1. 获取助手回复
    response = WriterAgent.chat(chat, user_input, on_token=_token)
    if not response:
        _status("[ERROR] Writer 无响应 — 请检查 API 密钥和网络连接")
        return False, [], 0

    code_blocks = chat.last_code_blocks
    if not code_blocks:
        return True, [], 0

    # 2. 逐个测试代码块，带自动修正
    passed_blocks: list[str] = []
    total_attempts = 0

    for idx, code in enumerate(code_blocks, 1):
        if len(code_blocks) > 1:
            _status(f"--- 代码块 {idx}/{len(code_blocks)} ---")

        for attempt in range(Config.MAX_ITERATIONS):
            total_attempts += 1
            _status(
                f"[Tester] {'执行' if attempt == 0 else f'修正第{attempt}次'}..."
            )

            success, msg = TesterAgent.execute(
                code, user_request=user_input
            )

            if success:
                _status(f"[OK] 测试通过！{msg}")
                if len(code_blocks) == 1:
                    WriterAgent.comment_on_result(
                        chat, msg, on_token=_token
                    )
                passed_blocks.append(code)
                break

            _status(f"[FAIL] {msg}")

            if attempt < Config.MAX_ITERATIONS - 1:
                _status("[Writer] 正在修正...")
                response = WriterAgent.retry_with_error(
                    chat, code, msg, on_token=_token
                )
                new_blocks = chat.last_code_blocks
                if new_blocks:
                    code = new_blocks[-1]
                else:
                    break
            else:
                _status(
                    f"[STOP] 已达最大修正轮数"
                    f" ({Config.MAX_ITERATIONS})，放弃此代码块。"
                )

    all_passed = len(passed_blocks) == len(code_blocks)
    return all_passed, passed_blocks, total_attempts
