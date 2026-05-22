# Code Collaboration Assistant · 双智能体代码协作助手

A dual-agent coding assistant with a Writer-Tester feedback loop — generates code from natural language, executes it, and auto-fixes errors. Supports any OpenAI-compatible API.

一个基于 Writer-Tester 闭环反馈的双智能体代码协作助手——用自然语言描述需求，自动生成代码、执行验证、修正错误。兼容任意 OpenAI 格式的 API。

---

## ✨ Features · 功能

- **Conversational AI** — Friendly, natural dialogue. Explains approach before writing code.
- **Streaming Output** — Tokens appear in real-time, like a chat.
- **Auto Code Extraction** — Detects ` ```python ``` ` blocks and executes them automatically.
- **Auto-Fix Loop** — On failure, Tester feeds errors back to Writer for automatic correction (up to N rounds).
- **Multi-Turn Memory** — Full conversation history preserved across turns.
- **Slash Commands** — `/model`, `/config`, `/history`, `/save`, `/exit`, etc.
- **Batch Testing** — Run multiple requests from a file, get pass/fail stats.

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
# Copy the template
copy .env.example .env        # Windows
cp .env.example .env          # macOS/Linux
```

Edit `.env` and fill in your credentials. **Defaults point to DeepSeek — swap to any OpenAI-compatible provider:**

```env
# --- DeepSeek (default) ---
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-v4-pro

# --- Alternative: OpenAI ---
# DEEPSEEK_API_KEY=sk-your-openai-key
# DEEPSEEK_BASE_URL=https://api.openai.com/v1/chat/completions
# DEEPSEEK_MODEL=gpt-4o

# --- Alternative: local Ollama ---
# DEEPSEEK_API_KEY=ollama
# DEEPSEEK_BASE_URL=http://localhost:11434/v1/chat/completions
# DEEPSEEK_MODEL=codellama

MAX_ITERATIONS=3
```

Despite the `DEEPSEEK_` prefix, the client follows the standard OpenAI chat completions format — any compatible endpoint works.

### 3. Run · 运行

```bash
python -m src.main                  # Interactive mode
python -m src.main -r "write a prime checker"
python -m src.main -r "写一个判断质数的函数" -q
python -m src.main -b requests.txt  # Batch mode
```

---

## ⌨️ Slash Commands · 斜杠指令

| Command | Description |
|---------|-------------|
| `/exit`, `/q` | Exit program |
| `/model <name>` | Switch model |
| `/models` | List available models |
| `/config` | Show current configuration |
| `/history` | Show conversation history |
| `/clear` | Reset conversation |
| `/save <path>` | Save last generated code to file |
| `/iterations <n>` | Set max fix rounds (1-10) |
| `/help`, `/?` | Show help |

---

## 📁 Project Structure · 项目结构

```
src/
├── main.py            # Entry point & CLI
├── shell.py           # Interactive REPL & slash commands
├── chat.py            # Conversation session & system prompt
├── config.py          # Configuration (reads from .env)
├── llm_client.py      # OpenAI-compatible API client (streaming)
├── utils.py           # Code block extraction
└── agents/
    ├── writer.py      # Writer Agent — conversational code generation
    └── tester.py      # Tester Agent — safe execution & auto-validation
```

---

## ⚙️ Environment Variables · 环境变量

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | — | **Required.** Your API key |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/chat/completions` | Chat completions endpoint |
| `DEEPSEEK_MODEL` | `deepseek-v4-pro` | Model name |
| `MAX_ITERATIONS` | `3` | Max correction rounds per request |

The variable names use `DEEPSEEK_` for historical reasons, but they accept any OpenAI-compatible API — just point `BASE_URL` and `MODEL` to your provider of choice.

---

## 🔌 Supported Backends · 支持的模型后端

Any API that follows the OpenAI `/v1/chat/completions` format will work out of the box:

| Provider | Example BASE_URL |
|----------|-----------------|
| DeepSeek | `https://api.deepseek.com/chat/completions` |
| OpenAI | `https://api.openai.com/v1/chat/completions` |
| Ollama (local) | `http://localhost:11434/v1/chat/completions` |
| vLLM / TGI | `http://your-server:8000/v1/chat/completions` |
| Any OpenAI-compatible proxy | Your custom URL |

---

## 🛡️ Security · 安全

- `.env` is gitignored — your API key stays local. `.env` 已被 `.gitignore` 排除，密钥不会上传。
- Code execution uses an isolated namespace. This is a prototype — consider sandboxing for production. 代码执行使用隔离命名空间，原型验证可接受，生产环境建议更安全的沙箱方案。

---

## 📝 License

MIT License — open to use, modify, and share.
