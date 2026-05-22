from __future__ import annotations

import io
import sys
import traceback
import re
import inspect


class TesterAgent:
    """Tester Agent：执行代码并自动验证已定义的函数"""

    @staticmethod
    def _find_functions(code: str) -> list[str]:
        pattern = re.compile(r"^def\s+(\w+)\s*\(", re.MULTILINE)
        return pattern.findall(code)

    @staticmethod
    def _build_test_for(func_name: str, func: object, req: str) -> str:
        try:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            param_count = len(params)
        except (ValueError, TypeError):
            params = []
            param_count = 0

        req_lower = req.lower()

        if param_count == 0:
            return f"print(repr({func_name}()))"

        if param_count == 1:
            if any(kw in req_lower for kw in ("质数", "prime")):
                return (
                    f"print(f'{func_name}(7)={{{func_name}(7)}}, "
                    f"{func_name}(10)={{{func_name}(10)}}')"
                )
            if any(kw in req_lower for kw in ("排序", "sort")):
                return f"print(repr({func_name}([3, 1, 2])))"
            if any(kw in req_lower for kw in ("反转", "reverse")):
                return f"print(repr({func_name}('hello')))"
            if any(kw in req_lower for kw in ("去重", "dup", "dedup")):
                return f"print(repr({func_name}([1, 2, 2, 3])))"
            if any(kw in req_lower for kw in ("斐波", "fib")):
                return f"print(f'{func_name}(10)={{{func_name}(10)}}')"
            if any(kw in req_lower for kw in ("阶乘", "factorial", "fact")):
                return f"print(f'{func_name}(5)={{{func_name}(5)}}')"
            return f"print(repr({func_name}(42)))"

        if param_count == 2:
            return (
                f"print(f'{func_name}(2, 3)="
                f"{{{func_name}(2, 3)}}')"
            )

        args = ", ".join(f"'{p}'" for p in params[:3])
        return f"print(repr({func_name}({args})))"

    @staticmethod
    def execute(code: str, user_request: str = "") -> tuple[bool, str]:
        old_stdout = sys.stdout
        captured = io.StringIO()

        try:
            sys.stdout = captured
            compiled = compile(code, "<generated>", "exec")
            namespace: dict = {}
            exec(compiled, {"__builtins__": __builtins__}, namespace)
            output = captured.getvalue()

            funcs = TesterAgent._find_functions(code)

            summary: list[str] = []
            if output.strip():
                summary.append(f"[stdout] {output.strip()}")

            if funcs:
                summary.append("[auto-test] 检测到函数，执行测试用例：")
                for name in funcs:
                    func = namespace.get(name)
                    if not callable(func):
                        continue

                    test_expr = TesterAgent._build_test_for(
                        name, func, user_request
                    )

                    capture2 = io.StringIO()
                    old_stdout2 = sys.stdout
                    try:
                        sys.stdout = capture2
                        test_env = dict(namespace)
                        test_env["__builtins__"] = __builtins__
                        exec(test_expr, test_env)
                        test_out = capture2.getvalue().strip()
                    except Exception as e:
                        test_out = f"[error] {e}"
                    finally:
                        sys.stdout = old_stdout2
                        capture2.close()

                    try:
                        sig_str = str(inspect.signature(func))
                    except (ValueError, TypeError):
                        sig_str = "(*)"

                    summary.append(
                        f"  {name}{sig_str}: "
                        f"{test_expr} → {test_out}"
                    )

                return True, "\n".join(summary)

            result = (
                output.strip()
                if output.strip()
                else "执行成功（无输出，且未检测到函数定义）"
            )
            return True, result
        except Exception:
            tb = traceback.format_exc()
            return False, tb
        finally:
            sys.stdout = old_stdout
            captured.close()
