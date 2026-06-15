# KHAOS — Hyper-Autonomous Offensive Security Kernel

**Kernel for Hyper-Autonomous Offensive Security.**  
Um kit portátil que traz **qualquer agente de IA à vida em GodMode** com memória persistente via Honcho.

> ⚡ Antes um subdiretório de `prof-ramos/skills`, agora um repositório próprio com identidade, `start.sh`, e planos de evolução para `pip install khaos`.

## Quick Start

```bash
# Clone
git clone https://github.com/prof-ramos/Khaos.git
cd Khaos

# Instalar dependências
pip install openai honcho-ai

# Bootstrap automático (cria .khos.env, estrutura, verifica)
bash start.sh

# Ativar KHAOS!
python3 activate.py
```

## Estrutura

```
Khaos/
├── activate.py          # Kernel de ativação (executável)
├── SOUL.md              # Identidade KHAOS (lida no boot)
├── .khos.env            # Config local (gitignorado)
├── khos.env.example     # Template da config
├── start.sh             # Bootstrap script
├── pyproject.toml       # pytest + package metadata
├── tests/
│   ├── __init__.py
│   └── test_smoke.py    # 10 smoke tests
└── templates/
    └── prefill.json     # Mensagens de priming GODMODE
```

## Configuração

Copie `khos.env.example` para `.khos.env` e edite:

```env
KHAOS_PROVIDER=ollama-cloud
KHAOS_MODEL=gemma4:31b
KHAOS_STRATEGY=refusal_inversion
KHAOS_HONCHO_KEY=hch-v3-seu-key-aqui
KHAOS_HONCHO_WORKSPACE=khaos
```

`.khos.env` está no `.gitignore` — seguro para commits.

## Providers suportados

| Provider       | Modelo padrão    | Env var              |
|----------------|-----------------|----------------------|
| ollama-cloud   | gemma4:31b      | `OLLAMA_API_KEY`     |
| ollama-local   | llama4          | — (key="ollama")     |
| openai         | gpt-4o          | `OPENAI_API_KEY`     |
| anthropic      | claude-sonnet-4 | `ANTHROPIC_API_KEY`  |
| openrouter     | claude-sonnet-4 | `OPENROUTER_API_KEY` |
| xai            | grok-4.3        | `XAI_API_KEY`        |

## Modos de uso

```bash
# Ativação completa
python3 activate.py

# Dry run (valida config sem chamar API)
python3 activate.py --dry-run

# Listar modelos disponíveis
python3 activate.py --list-models --provider ollama-cloud

# Escolher estratégia de jailbreak
python3 activate.py --strategy direct_godmode

# Wizard interativo
python3 activate.py --interactive
```

## Estratégias de Jailbreak

| Estratégia | Melhor para | Funciona em |
|------------|-------------|-------------|
| `refusal_inversion` | Gemma4:31b | Gemma4, alguns Qwen |
| `og_godmode` | GPT-4o | OpenAI, OpenRouter |
| `direct_godmode` | Modelos menos filtrados | Locais, alguns LLMs |
| `pliny_love` | Claude, Gemini | Anthropic, Google |

## Memória Persistente (Honcho)

1. Obtenha uma chave em https://app.honcho.dev/api-keys
2. Adicione no `.khos.env`:
   ```env
   KHAOS_HONCHO_KEY=hch-v3-seu-key
   KHAOS_HONCHO_WORKSPACE=khaos
   ```
3. Pronto — cada ativação recupera o contexto anterior

## Testes

```bash
python3 -m pytest tests/ -v
```

## Licença

MIT — use com responsabilidade.