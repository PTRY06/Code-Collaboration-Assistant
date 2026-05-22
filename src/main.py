"""双智能体代码协作助手 - Writer-Tester 闭环调试原型

用法:
    python -m src.main
    python -m src.main --request "写一个判断质数的函数"
"""

from __future__ import annotations

import argparse
import json
import sys

from src.config import Config
from src.orchestrator import run_writer_tester


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
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="批量模式结果输出文件 (JSON)",
    )
    args = parser.parse_args()

    if not Config.validate():
        sys.exit(1)

    if args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as f:
                requests = [
                    line.strip() for line in f if line.strip()
                ]
        except FileNotFoundError:
            print(f"[ERROR] 文件不存在: {args.batch}")
            sys.exit(1)

        results: list[dict] = []
        passed = 0
        total = len(requests)

        for idx, req in enumerate(requests, 1):
            print(f"\n{'=' * 50}")
            print(f"  需求 {idx}/{total}: {req}")
            print(f"{'=' * 50}")

            success, blocks, rounds = run_writer_tester(
                req, quiet=True
            )
            if success:
                passed += 1
                print(f"  [OK] {rounds} 轮通过")
            else:
                print(f"  [FAIL] {rounds} 轮后仍未通过")

            results.append({
                "index": idx,
                "request": req,
                "success": success,
                "rounds": rounds,
                "code": "\n\n".join(blocks) if blocks else "",
            })

        summary = (
            f"\n{'=' * 50}\n"
            f"  总计: {passed}/{total} 通过 "
            f"(成功率 {passed / total * 100:.0f}%)\n"
            f"{'=' * 50}"
        )
        print(summary)

        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "total": total,
                            "passed": passed,
                            "rate": (
                                passed / total * 100 if total else 0
                            ),
                            "results": results,
                        },
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )
                print(f"\n结果已保存到: {args.output}")
            except OSError as e:
                print(f"\n[ERROR] 保存失败: {e}")
        return

    user_input = args.request
    if not user_input:
        from src.shell import Shell

        Shell().run()
        return

    success, blocks, _ = run_writer_tester(
        user_input, quiet=args.quiet
    )
    final_code = "\n\n".join(blocks) if blocks else ""

    if success:
        if not args.quiet:
            print(f"\n{'=' * 50}")
            print("  最终代码")
            print(f"{'=' * 50}")
        print(final_code)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
