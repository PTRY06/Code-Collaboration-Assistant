# Code Collaboration Assistant · 双智能体代码协作助手

A dual-agent coding assistant that uses the Write↙Tester feedback loop to automatically generate, execute, and fix Python code powered by DeepSeek API.

一个基于 Writer-Tester 闭环反馈的双智能体代码协作助手，使用 DeepSeek API 驱动，自动生成、执行并修正 Python 代码。

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

### 2. Configure API Key · 配置密钥

```bash
# Copy the template
copy .env.example .env        # Windows
cp .env.example .env          # macOS/Linux

# Edit .env and replace with your real key
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

Get a key at [platform.deepseek.com](https://platform.deepseek.com).

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
| `/model <name>` | Switch model (`deepseek-v4-pro`, `deepseek-v4-flash`) |
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
├── shell.py           # Interactive REPL shell
├── chat.py            # Conversation session & system prompt
├── config.py          # Configuration (reads from .env)
├── llm_client.py      # DeepSeek API client (streaming support)
├── utils.py           # Code block extraction
└── agents/
    ├── writer.py      # Writer Agent — conversational code generation
    └── tester.py      # Tester Agent — safe execution & auto-validation
```

---

## ⚙️ Environment Variables · 环境变量

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | — | **Required.** Your DeepSeek API key |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/chat/completions` | API endpoint |
| `DEEPSEEK_MODEL` | `deepseek-v4-pro` | Model name |
| `MAX_ITERATIONS` | `3` | Max Writer-Tester correction rounds |

---

## 🛡️ Security · 安全

- `.env` is gitignored — your API key stays local.
- Code execution uses an isolated namespace. Not for production use; consider sandboxing for public-facing deployments.
- `.env` 已被 `.gitignore` 排除，密钥不会上传。
- 代码执行使用隔离命名空间，原型验证可接受，生产环境建议更安全的沙箱方案。

---

## 📝 License

MIT License — open to use, modify, and share.
