# Code Collaboration Assistant · 双智能体代码协作助手

A dual-agent coding assistant with a Writer-Tester feedback loop — generates code from natural language, executes it, and auto-fixes errors. Supports any OpenAI-compatible API.

一个基于 Writer-Tester 闭环反馈的双智能体代码协作助手——用自然语言描述需求，自动生成代码、执行验证、修正错误。兼容任意 OpenAI 格式的 API。

---

## ✨ Features · 功能

- **Conversational AI · 对话式 AI** — Friendly, natural dialogue. Explains approach before writing code. 在写代码前先解释思路，像朋友一样自然对话。
- **Streaming Output · 流式输出** — Tokens appear in real-time, like a chat. 逐字实时显示，如打字机效果。
- **Auto Code Extraction · 自动代码提取** — Detects ` ```python ``` ` blocks and executes them automatically. 自动识别代码块并执行。
- **Auto-Fix Loop · 自动修正闭环** — On failure, Tester feeds errors back to Writer for automatic correction (up to N rounds). 代码出错时自动反馈给 Writer 修正，最多 N 轮。
- **Multi-Turn Memory · 多轮对话记忆** — Full conversation history preserved across turns, with auto-trimming when approaching context limits. 完整保留对话上下文，超出限制时自动裁剪旧消息。
- **Sandbox Execution · 沙箱执行** — Code runs in an isolated subprocess with a configurable timeout. 代码在隔离子进程中执行，支持超时限制。
- **Slash Commands · 斜杠指令** — `/model`, `/config`, `/history`, `/save`, `/exit` and more. 支持 `/model`、`/config` 等交互指令。
- **Batch Testing · 批量测试** — Run multiple requests from a file, get pass/fail stats. 从文件批量读取需求，输出通过率统计。

---

## 🚀 Quick Start · 快速开始

### 1. Clone & Install · 克隆并安装

```bash
git clone https://github.com/PTRY06/Code-Collaboration-Assistant.git
cd Code-Collaboration-Assistant
pip install -r requirements.txt
```

### 2. Configure · 配置

```bash
# Copy the template · 复制模板
copy .env.example .env        # Windows
cp .env.example .env          # macOS/Linux
```

Edit `.env` and fill in your credentials. 编辑 `.env` 填入你的 API 凭证。

**Defaults point to DeepSeek — swap to any OpenAI-compatible provider. 默认使用 DeepSeek，可替换为任意 OpenAI 兼容服务：**

```env
# --- DeepSeek (default · 默认) ---
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-v4-pro

# --- Alternative: OpenAI · 替代：OpenAI ---
# DEEPSEEK_API_KEY=sk-your-openai-key
# DEEPSEEK_BASE_URL=https://api.openai.com/v1/chat/completions
# DEEPSEEK_MODEL=gpt-4o

# --- Alternative: local Ollama · 替代：本地 Ollama ---
# DEEPSEEK_API_KEY=ollama
# DEEPSEEK_BASE_URL=http://localhost:11434/v1/chat/completions
# DEEPSEEK_MODEL=codellama

# Tuning · 调参
MAX_ITERATIONS=3
MAX_RETRIES=3
SANDBOX_TIMEOUT=10
MAX_HISTORY_TOKENS=96000
TEMPERATURE=0.2
TIMEOUT=60
```

Despite the `DEEPSEEK_` prefix, the client follows the standard OpenAI chat completions format — any compatible endpoint works. 变量名虽含 `DEEPSEEK_`，但客户端遵循标准 OpenAI 格式，任何兼容端点均可使用。

### 3. Run · 运行

```bash
# Interactive REPL with slash commands · 交互式 REPL
python -m src.main

# Single request — generates, tests, and auto-fixes · 单次请求
python -m src.main -r "write a function to check if a number is prime"
python -m src.main -r "写一个函数反转字符串" -q

# Batch test from file · 从文件批量测试
python -m src.main -b examples.txt -o results.json
```

Example batch file (`examples.txt`) · 示例批量文件：

```
write a function to remove duplicates from a list
generate a Fibonacci sequence up to n terms
写一个函数判断回文字符串
create a function that sorts a list of dictionaries by a given key
```

---

## ⌨️ Slash Commands · 斜杠指令

| Command · 指令 | Description · 说明 |
|----------------|-------------------|
| `/exit`, `/q` | Exit program · 退出程序 |
| `/model <name>` | Switch model · 切换模型 |
| `/models` | List available models · 列出可用模型 |
| `/config` | Show current configuration · 显示当前配置 |
| `/history` | Show conversation history · 显示对话历史 |
| `/clear` | Reset conversation · 重置对话 |
| `/save <path>` | Save last generated code to file · 保存最后生成的代码 |
| `/iterations <n>` | Set max fix rounds (1-10) · 设置最大修正轮数 |
| `/help`, `/?` | Show help · 显示帮助 |

---

## 📁 Project Structure · 项目结构

```
src/
├── main.py            # Entry point & CLI · 入口与命令行
├── shell.py           # Interactive REPL & slash commands · 交互式 Shell
├── chat.py            # Conversation session & auto-trimming · 对话管理
├── config.py          # Configuration (reads from .env) · 配置管理
├── llm_client.py      # API client with retry & streaming · API 客户端
├── utils.py           # Code block extraction · 代码块提取
└── agents/
    ├── writer.py      # Writer Agent — conversational code gen · 对话生成
    └── tester.py      # Tester Agent — sandbox execution · 沙箱执行
```

---

## ⚙️ Environment Variables · 环境变量

| Variable · 变量 | Default · 默认值 | Description · 说明 |
|----------------|-----------------|-------------------|
| `DEEPSEEK_API_KEY` | — | **Required.** Your API key · **必填。** API 密钥 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/chat/completions` | Chat completions endpoint · 聊天补全端点 |
| `DEEPSEEK_MODEL` | `deepseek-v4-pro` | Model name · 模型名称 |
| `MAX_ITERATIONS` | `3` | Max correction rounds · 最大修正轮数 |
| `MAX_RETRIES` | `3` | API retry attempts on failure · API 失败重试次数 |
| `RETRY_BACKOFF_FACTOR` | `1.5` | Exponential backoff multiplier · 指数退避因子 |
| `SANDBOX_TIMEOUT` | `10` | Code execution timeout (seconds) · 代码执行超时（秒） |
| `MAX_HISTORY_TOKENS` | `96000` | Auto-trim threshold for chat history · 对话历史自动裁剪阈值 |
| `TEMPERATURE` | `0.2` | LLM sampling temperature · 模型采样温度 |
| `TIMEOUT` | `60` | API request timeout (seconds) · API 请求超时（秒） |

The variable names use `DEEPSEEK_` for historical reasons, but they accept any OpenAI-compatible API — just point `BASE_URL` and `MODEL` to your provider of choice. 变量名中 `DEEPSEEK_` 仅为历史遗留，可替换为任意 OpenAI 兼容 API。

---

## 🔌 Supported Backends · 支持的模型后端

Any API that follows the OpenAI `/v1/chat/completions` format will work out of the box. 任意兼容 OpenAI `/v1/chat/completions` 格式的 API 均可直接使用。

| Provider · 提供商 | Example BASE_URL · 示例端点 |
|-------------------|---------------------------|
| DeepSeek | `https://api.deepseek.com/chat/completions` |
| OpenAI | `https://api.openai.com/v1/chat/completions` |
| Ollama (local · 本地) | `http://localhost:11434/v1/chat/completions` |
| vLLM / TGI | `http://your-server:8000/v1/chat/completions` |
| Any OpenAI-compatible proxy · 任意兼容代理 | Your custom URL · 自定义地址 |

---

## 🛡️ Security · 安全

- `.env` is gitignored — your API key stays local and will never be committed. `.env` 已被 `.gitignore` 排除，密钥不会上传至仓库。
- Code execution uses subprocess isolation with a configurable timeout. This is a prototype — consider Docker or further sandboxing for production deployments. 代码执行采用子进程隔离 + 可配置超时，原型验证可接受，生产环境建议 Docker 或更严格沙箱。

---

## 📝 License · 许可证

MIT License — open to use, modify, and share. MIT 许可证——自由使用、修改和分发。
