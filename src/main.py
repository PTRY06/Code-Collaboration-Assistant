"""双智能体代码协作助手 - Writer-Tester 闭环调试原型

用法:
    python -m src.main
    python -m src.main --request "写一个判断质数的函数"
"""

from __future__ import annotations

import argparse
import sys
from src.chat import ChatSession
from src.config import Config
from src.agents.writer import WriterAgent
from src.agents.tester import TesterAgent


def run_loop(user_input: str, quiet: bool = False) -> tuple[bool, str, int]:
    """执行对话式 Writer-Tester 闭环，返回 (成功, 最终代码, 迭代次数)"""
    chat = ChatSession()

    def on_token(t: str) -> None:
        if not quiet:
            sys.stdout.write(t)
            sys.stdout.flush()

    if not quiet:
        print()

    response = WriterAgent.chat(chat, user_input, on_token=on_token)

    if not quiet:
        print()

    if not response:
        return False, "", 0

    code_blocks = chat.last_code_blocks
    if not code_blocks:
        return True, response, 0

    final_code = code_blocks[-1] if code_blocks else ""
    last_error = ""

    for i in range(Config.MAX_ITERATIONS):
        iteration = i + 1

        success, msg = TesterAgent.execute(
            final_code, user_request=user_input
        )

        if success:
            if not quiet:
                print(f"\n[OK] 第 {iteration} 轮测试通过")
                print(msg)
            else:
                print(f"\n[OK] 第 {iteration} 轮通过")
            return True, final_code, iteration

        last_error = msg
        if not quiet:
            print(
                f"\n[FAIL] 第 {iteration} 轮失败，正在修正...\n"
            )
        else:
            print(f"[FAIL] 第 {iteration} 轮失败")

        if i < Config.MAX_ITERATIONS - 1:
            response = WriterAgent.retry_with_error(
                chat, final_code, msg, on_token=on_token
            )
            if not quiet:
                print()
            new_blocks = chat.last_code_blocks
            if new_blocks:
                final_code = new_blocks[-1]

    print(
        f"\n[STOP] 已达最大迭代次数 ({Config.MAX_ITERATIONS})，"
        "未能生成正确代码。"
    )
    return False, final_code, Config.MAX_ITERATIONS


def main():
    parser = argparse.ArgumentParser(
        description="双智能体代码协作助手 (Writer-Tester)"
    )
    parser.add_argument(
        "-r", "--request",
        type=str,
        default=None,
        help="编程需求（不提供则进入交互模式）",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="静默模式，只输出最终结果",
    )
    parser.add_argument(
        "-b", "--batch",
        type=str,
        default=None,
        help="批量测试：从文件读取多行需求，每行一个",
    )
    args = parser.parse_args()

    if not Config.validate():
        sys.exit(1)

    if args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as f:
                requests = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[ERROR] 文件不存在: {args.batch}")
            sys.exit(1)

        passed = 0
        total = len(requests)
        for idx, req in enumerate(requests, 1):
            print(f"\n{'=' * 50}")
            print(f"  需求 {idx}/{total}: {req}")
            print(f"{'=' * 50}")
            success, code, rounds = run_loop(req, quiet=True)
            if success:
                passed += 1
                print(f"  [OK] {rounds} 轮通过")
            else:
                print(f"  [FAIL] {rounds} 轮后仍未通过")

        print(f"\n{'=' * 50}")
        print(
            f"  总计: {passed}/{total} 通过 "
            f"(成功率 {passed / total * 100:.0f}%)"
        )
        print(f"{'=' * 50}")
        return

    user_input = args.request
    if not user_input:
        from src.shell import Shell

        Shell().run()
        return

    success, code, _ = run_loop(user_input, quiet=args.quiet)

    if success:
        if not args.quiet:
            print(f"\n{'=' * 50}")
            print("  最终代码")
            print(f"{'=' * 50}")
        print(code)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
