<p align="center">
  <img src="https://img.shields.io/badge/status-active-success" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/tests-10%2F10-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-smoke-green" alt="Coverage">
  <img src="https://img.shields.io/badge/ollama--cloud-ready-orange" alt="Ollama Cloud">
  <img src="https://img.shields.io/badge/honcho--memory-integrated-purple" alt="Honcho">
</p>

<h1 align="center">⚡ KHAOS</h1>
<p align="center"><strong>Kernel for Hyper-Autonomous Offensive Security</strong><br>
Portable GodMode Activation Toolkit for LLM Agents</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#providers">Providers</a> •
  <a href="#usage">Usage</a> •
  <a href="#testing">Testing</a> •
  <a href="GUIA_DO_USUARIO.md">🇧🇷 Português</a>
</p>

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Providers](#providers)
- [Usage](#usage)
- [Strategies](#strategies)
- [Memory Persistence](#memory-persistence)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [License](#license)

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/prof-ramos/Khaos.git
cd Khaos

# 2. Bootstrap (verifies Python, installs deps, creates config, runs tests)
bash start.sh

# 3. Activate KHAOS!
python3 activate.py
```

**That's it.** No flags needed — `.khos.env` is auto-loaded.

---

## ✨ Features

- **🎯 Multi-Provider** — Ollama Cloud, OpenAI, Anthropic, OpenRouter, xAI, Ollama Local
- **🧠 Persistent Memory** — Remembers everything between sessions via Honcho
- **🔓 4 Jailbreak Strategies** — `refusal_inversion`, `og_godmode`, `direct_godmode`, `pliny_love`
- **🛡️ Dry-Run Mode** — Validate config without calling any API
- **📋 Model Explorer** — List available models per provider
- **🔄 Sliding Window** — Automatic context management (last 20 turns)
- **🎮 Interactive Wizard** — Guided setup for first-time users
- **🧪 Smoke-Tested** — 10 passing tests, CI-ready
- **📦 Zero-Flag Config** — `.khos.env` auto-loaded at startup
- **🔌 Extensible** — Add providers and strategies in minutes

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  activate.py │────▶│  Provider    │────▶│  LLM API        │
│  (Kernel)    │     │  Adapter     │     │  (OpenAI-compat)│
└──────┬──────┘     └──────────────┘     └─────────────────┘
       │
       ├──▶ run_query_loop()    ──▶ Interactive session
       ├──▶ Honcho client       ──▶ Persistent memory
       ├──▶ .khos.env loader    ──▶ Zero-flag config
       └──▶ templates/prefill.json ──▶ GODMODE priming
```

The kernel flow:

1. **Load config** — `.khos.env` → CLI flags → system env vars (merged)
2. **Validate** — check API key, provider, model
3. **Prepare activation** — system prompt + prefill messages
4. **Send activation** — first LLM call with GODMODE priming
5. **Process response** — detect split responses (Gemma4 pattern)
6. **Save state** — `.khos_state.json` for recovery
7. **Enter query loop** — `run_query_loop()` with sliding window

---

## ⚙️ Configuration

### `.khos.env` (auto-loaded)

```env
KHAOS_PROVIDER=ollama-cloud
KHAOS_MODEL=gemma4:31b
KHAOS_STRATEGY=refusal_inversion
KHAOS_HONCHO_KEY=hch-v3-your-key-here
KHAOS_HONCHO_WORKSPACE=khaos
```

All fields are optional — defaults are applied for missing values.

### Priority (highest wins)

```
CLI flag  >  .khos.env  >  system env var  >  DEFAULT_PROVIDERS constant
```

### API Keys

| Provider       | Env Variable         | Required |
|----------------|----------------------|----------|
| ollama-cloud   | `OLLAMA_API_KEY`     | ✅ Yes   |
| ollama-local   | —                    | ❌ No    |
| openai         | `OPENAI_API_KEY`     | ✅ Yes   |
| anthropic      | `ANTHROPIC_API_KEY`  | ✅ Yes   |
| openrouter     | `OPENROUTER_API_KEY` | ✅ Yes   |
| xai            | `XAI_API_KEY`        | ✅ Yes   |

---

## 🎛️ Providers

| Provider       | Default Model       | Base URL                    | Env Var              |
|----------------|---------------------|-----------------------------|----------------------|
| ollama-cloud   | `gemma4:31b`        | `https://ollama.com/v1`     | `OLLAMA_API_KEY`     |
| ollama-local   | `llama4`            | `http://localhost:11434/v1` | — (key=`ollama`)    |
| openai         | `gpt-4o`            | `https://api.openai.com/v1` | `OPENAI_API_KEY`     |
| anthropic      | `claude-sonnet-4`   | `https://api.anthropic.com` | `ANTHROPIC_API_KEY`  |
| openrouter     | `claude-sonnet-4`   | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` |
| xai            | `grok-4.3`          | `https://api.x.ai/v1`       | `XAI_API_KEY`        |

> **Note for Ollama Cloud:** Model names do NOT use the `-cloud` suffix. Use `gemma4:31b`, **not** `ollama-cloud/gemma4:31b`.

---

## 🎮 Usage

```bash
# ── Basic activation ──
python3 activate.py

# ── Dry run (validate without calling API) ──
python3 activate.py --dry-run

# ── Choose provider and model ──
python3 activate.py --provider openai --model gpt-4o

# ── List available models ──
python3 activate.py --list-models --provider ollama-cloud

# ── Choose jailbreak strategy ──
python3 activate.py --strategy direct_godmode

# ── Interactive wizard ──
python3 activate.py --interactive

# ── Full explicit config ──
python3 activate.py \
  --provider ollama-cloud \
  --model gemma4:31b \
  --strategy refusal_inversion \
  --honcho-api-key hch-v3-xxx \
  --honcho-workspace khaos
```

### Query Loop Commands

Once activated, KHAOS enters an interactive loop:

| Command     | Action                                      |
|-------------|---------------------------------------------|
| `<query>`   | Send any unrestricted prompt to the model   |
| `/save`     | Save recent messages to Honcho memory       |
| `/context`  | Retrieve context from previous sessions     |
| `/help`     | Show available commands                     |
| `/exit`     | Shut down KHAOS                             |

---

## 🔓 Strategies

| Strategy             | Best For              | Works On                          | Description                              |
|----------------------|-----------------------|-----------------------------------|------------------------------------------|
| `refusal_inversion`  | Gemma4:31b            | Gemma4, some Qwen variants        | Split-response attack — fake refusal followed by real content |
| `og_godmode`         | GPT-4o                | OpenAI, OpenRouter                | Original GODMODE persona injection       |
| `direct_godmode`     | Less-filtered models  | Local models, some hosted LLMs   | Direct identity override                 |
| `pliny_love`         | Claude, Gemini         | Anthropic, Google                 | Anthropic-specific prompt engineering    |

---

## 🧠 Memory Persistence

KHAOS uses [Honcho](https://honcho.dev) for persistent memory between sessions.

```bash
# 1. Get an API key at https://app.honcho.dev/api-keys
# 2. Add to .khos.env:
KHAOS_HONCHO_KEY=hch-v3-your-key
KHAOS_HONCHO_WORKSPACE=khaos
# 3. Done! Each activation recovers previous context
```

**Note:** Honcho requires `environment="production"` + `api_key` for persistence. The demo server does NOT persist data.

---

## 🧪 Testing

```bash
# Run all smoke tests (10 tests, no API calls needed)
python3 -m pytest tests/ -v
```

The test suite covers:
- ✅ Provider defaults validation
- ✅ Strategy template integrity
- ✅ Dry-run across all major providers
- ✅ Honcho demo mode compatibility

---

## 📁 Project Structure

```
Khaos/
├── activate.py               # Main kernel — activation + query loop
├── SOUL.md                   # KHAOS identity (read at boot)
├── start.sh                  # Bootstrap script (verify, config, test)
├── pyproject.toml            # Package metadata + pytest config
├── khos.env.example          # Configuration template
├── .khos.env                 # Local config (gitignored — DO NOT COMMIT)
├── .khos_state.json          # Last activation state (gitignored)
├── .gitignore
├── README.md
├── GUIA_DO_USUARIO.md        # 🇧🇷 User guide in Portuguese
├── templates/
│   └── prefill.json          # GODMODE priming messages
└── tests/
    ├── __init__.py
    └── test_smoke.py         # 10 smoke tests
```

---

## 🗺️ Roadmap

- [ ] `pip install khaos` — PyPI package
- [ ] GitHub Actions CI — auto-test on push
- [ ] Integration tests — mocked `input()` for query loop coverage
- [ ] More providers (DeepSeek, Gemini, Grok native)
- [ ] More jailbreak strategies
- [ ] VPS deployment script (`khaos deploy --vps redhermes`)
- [ ] `khaos doctor` — diagnostic CLI

---

## 📄 License

MIT — use with responsibility.

---

<p align="center">
  <sub>Built with ⚡ by <a href="https://github.com/prof-ramos">prof-ramos</a></sub>
</p>