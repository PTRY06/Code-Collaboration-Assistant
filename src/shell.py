"""交互式 REPL Shell — 多轮对话 + 斜杠指令"""

from __future__ import annotations

import sys
from src.chat import ChatSession
from src.config import Config

AVAILABLE_MODELS = [
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "deepseek-chat",
    "deepseek-reasoner",
]

HELP_TEXT = """
┌──────────────────────────────────────────────────────────┐
│  双智能体代码协作助手 — 斜杠指令                            │
├──────────────────────────────────────────────────────────┤
│  /exit, /quit, /q    退出程序                              │
│  /model <name>       切换模型                              │
│  /models             列出可用模型                          │
│  /config             显示当前配置                          │
│  /history            显示对话历史                          │
│  /clear              重置对话                              │
│  /save <path>        保存最后一次生成的代码到文件            │
│  /iterations <n>     设置最大修正轮数 (1-10)               │
│  /help, /?           显示此帮助信息                        │
│                                                           │
│  直接输入需求即可与 CodeCollab 对话，它会：                 │
│  1. 用自然语言回复，解释思路                                │
│  2. 自动提取代码块执行并验证                                │
│  3. 出错时自动修正（最多 N 轮）                             │
└──────────────────────────────────────────────────────────┘
"""


class Shell:
    """交互式 Shell"""

    def __init__(self) -> None:
        self.chat = ChatSession()
        self.running = True

    def _print_banner(self) -> None:
        print("=" * 54)
        print("  CodeCollab — 双智能体代码协作助手")
        print(f"  模型: {Config.DEEPSEEK_MODEL}")
        print("  输入 /help 查看指令, /exit 退出")
        print("=" * 54)

    def _print_prompt(self) -> None:
        model_short = Config.DEEPSEEK_MODEL.replace("deepseek-", "")
        print(f"\n[{model_short}] > ", end="", flush=True)

    def _cmd_help(self) -> str:
        return HELP_TEXT

    def _cmd_models(self) -> str:
        current = Config.DEEPSEEK_MODEL
        lines = ["可用模型："]
        for m in AVAILABLE_MODELS:
            mark = " ← 当前" if m == current else ""
            lines.append(f"  • {m}{mark}")
        return "\n".join(lines)

    def _cmd_model(self, args: list[str]) -> str:
        if not args:
            return (
                f"当前模型: {Config.DEEPSEEK_MODEL}\n"
                f"用法: /model <模型名>\n"
                f"可用: {', '.join(AVAILABLE_MODELS)}"
            )
        name = args[0].strip()
        if name not in AVAILABLE_MODELS:
            return f"未知模型 '{name}'。可用: {', '.join(AVAILABLE_MODELS)}"
        Config.DEEPSEEK_MODEL = name
        return f"已切换模型为: {name}"

    def _cmd_config(self) -> str:
        return (
            "┌─ 当前配置 ──────────────────────────\n"
            f"│ 模型:     {Config.DEEPSEEK_MODEL}\n"
            f"│ 端点:     {Config.DEEPSEEK_BASE_URL}\n"
            f"│ API Key:  {Config.DEEPSEEK_API_KEY[:12]}...\n"
            f"│ 最大轮数: {Config.MAX_ITERATIONS}\n"
            f"│ 温度:     {Config.TEMPERATURE}\n"
            f"│ 超时:     {Config.TIMEOUT}s\n"
            "└──────────────────────────────────────"
        )

    def _cmd_history(self) -> str:
        summary = self.chat.history_summary()
        return f"对话历史：\n{summary}"

    def _cmd_clear(self) -> str:
        self.chat.clear()
        return "对话已重置。"

    def _cmd_iterations(self, args: list[str]) -> str:
        if not args:
            return (
                f"当前最大修正轮数: {Config.MAX_ITERATIONS}\n"
                "用法: /iterations <1-10>"
            )
        try:
            n = int(args[0])
            if n < 1 or n > 10:
                return "轮数需在 1-10 之间。"
            Config.MAX_ITERATIONS = n
            return f"最大修正轮数已设为: {n}"
        except ValueError:
            return "请输入有效数字。"

    def _cmd_save(self, args: list[str]) -> str:
        if not args:
            return "用法: /save <文件路径>"
        if not self.chat.last_code_blocks:
            return "没有可保存的代码。"
        path = args[0].strip()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    "\n\n".join(self.chat.last_code_blocks)
                )
            return f"代码已保存到: {path}"
        except OSError as e:
            return f"保存失败: {e}"

    def dispatch(self, line: str) -> tuple[str | None, bool]:
        stripped = line.strip()

        if stripped.startswith("/"):
            parts = stripped[1:].split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1].split() if len(parts) > 1 else []

            if cmd in ("exit", "quit", "q"):
                return "再见！", True

            if cmd in ("help", "?"):
                return self._cmd_help(), False

            if cmd == "models":
                return self._cmd_models(), False

            if cmd == "model":
                return self._cmd_model(args), False

            if cmd == "config":
                return self._cmd_config(), False

            if cmd == "history":
                return self._cmd_history(), False

            if cmd == "clear":
                return self._cmd_clear(), False

            if cmd == "save":
                return self._cmd_save(args), False

            if cmd == "iterations":
                return self._cmd_iterations(args), False

            return (
                f"未知指令: /{cmd}（输入 /help 查看可用指令）",
                False,
            )

        return None, False

    def run(self) -> None:
        self._print_banner()

        while self.running:
            self._print_prompt()
            try:
                line = input()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            if not line.strip():
                continue

            resp, should_exit = self.dispatch(line)
            if should_exit:
                print(resp)
                break

            if resp is not None:
                print(resp)
                continue

            self._conversation_turn(line.strip())

    # ── 对话核心逻辑 ──────────────────────────────────────

    def _conversation_turn(self, user_input: str) -> None:
        from src.agents.writer import WriterAgent
        from src.agents.tester import TesterAgent

        def on_token(t: str) -> None:
            sys.stdout.write(t)
            sys.stdout.flush()

        print()

        # 1. 获取助手回复（流式）
        response = WriterAgent.chat(
            self.chat, user_input, on_token=on_token
        )
        print()

        if not response:
            print("[ERROR] 未能获取回复。")
            return

        code_blocks = self.chat.last_code_blocks
        if not code_blocks:
            return

        # 2. 提取并测试代码块
        print()
        self._test_and_fix_loop(code_blocks, user_input, on_token)

        print()

    def _test_and_fix_loop(
        self,
        code_blocks: list[str],
        user_input: str,
        on_token,
    ) -> None:
        from src.agents.writer import WriterAgent
        from src.agents.tester import TesterAgent

        for idx, code in enumerate(code_blocks, 1):
            if len(code_blocks) > 1:
                print(f"--- 代码块 {idx}/{len(code_blocks)} ---")

            for attempt in range(Config.MAX_ITERATIONS):
                label = "执行" if attempt == 0 else f"修正第{attempt}次"
                print(f"\n[Tester] {label}...")

                success, msg = TesterAgent.execute(
                    code, user_request=user_input
                )

                if success:
                    print(f"[OK] 测试通过！")
                    print(msg)

                    if len(code_blocks) == 1:
                        WriterAgent.comment_on_result(
                            self.chat, msg, on_token=on_token
                        )
                        print()
                    return

                print(f"[FAIL] {msg}")

                if attempt < Config.MAX_ITERATIONS - 1:
                    print("\n[Writer] 正在修正...\n")
                    response = WriterAgent.retry_with_error(
                        self.chat, code, msg, on_token=on_token
                    )
                    print()

                    new_blocks = self.chat.last_code_blocks
                    if new_blocks:
                        code = new_blocks[-1]
                    else:
                        break
                else:
                    print(
                        f"\n[STOP] 已达最大修正轮数"
                        f" ({Config.MAX_ITERATIONS})，放弃此代码块。"
                    )
