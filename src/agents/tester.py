from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

from src.config import Config


class TesterAgent:
    """Tester Agent：子进程沙箱执行代码 + LLM 驱动测试用例生成"""

    @staticmethod
    def _find_functions(code: str) -> list[str]:
        pattern = re.compile(r"^def\s+(\w+)\s*\(", re.MULTILINE)
        return pattern.findall(code)

    @staticmethod
    def _generate_tests_via_llm(code: str, user_request: str) -> str:
        from src.llm_client import call_llm

        prompt = (
            "你是一个 Python 测试专家。下面是用户的需求和一段 Python 代码。\n"
            "请写一行 print() 语句来测试这段代码的核心函数。\n"
            "只输出一行 print 语句，不要任何解释、markdown 或额外代码。\n"
            "\n"
            f"用户需求: {user_request}\n"
            f"代码:\n```python\n{code}\n```\n"
        )
        response = call_llm(prompt)
        if not response:
            return ""

        clean = (
            response.strip()
            .replace("```python", "")
            .replace("```", "")
            .strip()
        )
        for prefix in ("print(", "print ("):
            idx = clean.find(prefix)
            if idx != -1:
                return clean[idx:].strip()
        return clean

    @staticmethod
    def execute(
        code: str, user_request: str = ""
    ) -> tuple[bool, str]:
        tmp_dir = None
        try:
            tmp_dir = tempfile.mkdtemp(prefix="cc_tester_")
            code_path = os.path.join(tmp_dir, "code.py")

            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)

            proc = subprocess.run(
                [sys.executable, code_path],
                capture_output=True,
                text=True,
                timeout=Config.SANDBOX_TIMEOUT,
                cwd=tmp_dir,
            )

            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                if stderr:
                    lines = stderr.split("\n")
                    short = "\n".join(lines[-6:])
                    return False, f"[stderr]\n{short}"
                return False, f"退出码 {proc.returncode}"

            stdout = proc.stdout.strip()
            summary: list[str] = []
            if stdout:
                summary.append(f"[stdout]\n{stdout}")

            funcs = TesterAgent._find_functions(code)

            if funcs:
                test_expr = TesterAgent._generate_tests_via_llm(
                    code, user_request
                )
                if test_expr:
                    test_code = (
                        f"import sys; sys.path.insert(0, '.')\n"
                        f"from code import *\n"
                        f"{test_expr}\n"
                    )
                    test_path = os.path.join(tmp_dir, "_test.py")
                    with open(test_path, "w", encoding="utf-8") as f:
                        f.write(test_code)

                    proc2 = subprocess.run(
                        [sys.executable, test_path],
                        capture_output=True,
                        text=True,
                        timeout=Config.SANDBOX_TIMEOUT,
                        cwd=tmp_dir,
                    )
                    test_out = (
                        proc2.stdout.strip()
                        if proc2.returncode == 0
                        else f"[error] {proc2.stderr.strip().split(chr(10))[-1]}"
                    )
                    summary.append(
                        f"[auto-test] {test_expr} → {test_out}"
                    )

                return True, "\n".join(summary) if summary else "执行成功（无输出）"

            return True, stdout if stdout else "执行成功（无输出，且未检测到函数定义）"

        except subprocess.TimeoutExpired:
            return False, f"执行超时（>{Config.SANDBOX_TIMEOUT}s）"
        except Exception as e:
            return False, str(e)
        finally:
            if tmp_dir and os.path.isdir(tmp_dir):
                import shutil

                try:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                except Exception:
                    pass
