# Plan 003: Adicionar `[project]` no pyproject.toml + entry point `khaos`

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise.
>
> **Drift check**: `git diff --stat ab25f4e..HEAD -- pyproject.toml activate.py`
> Se algum dos arquivos mudou, compare antes de prosseguir.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: Plan 002 (lazy env loading — import limpo é pré-requisito para `pip install`)
- **Category**: dx, enhancement
- **Planned at**: commit `ab25f4e`, 2026-06-15
- **Issue**: https://github.com/prof-ramos/Khaos/issues/3

## Why this matters

O `pyproject.toml` atual só tem `[build-system]` e config de pytest. Sem `[project]`, não é possível:
- `pip install .` ou `pip install -e .`
- Definir entry point CLI (`khaos activate`)
- Publicar no PyPI
- Declarar dependências oficialmente (agora ficam no README)

Isso impede o KHAOS de ser instalado como pacote Python — o único jeito é `python3 activate.py`.

## Current state

**pyproject.toml** (conteúdo completo):
```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.setuptools.packages.find]
where = ["."]
include = ["activate*"]
```

**activate.py** — o `if __name__ == "__main__":` (linha ~640) faz o parsing e chama `activate_khaos()`. Não há função `main()` separada.

Convenção do repositório: Python padrão, sem type hints. O entry point será `activate:main` — precisa criar uma função `main()`.

## Commands you will need

| Purpose                      | Command                                                    | Expected on success |
|------------------------------|------------------------------------------------------------|---------------------|
| Install editable             | `pip install -e .`                                         | exit 0 |
| CLI entry point              | `khaos --help`                                             | mostra help |
| CLI activate                 | `khaos --dry-run`                                          | "Dry run complete" |
| Compile                      | `python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"` | OK |
| Tests via installed pkg      | `python3 -m pytest tests/ -v`                              | 10/10 pass |
| Tests via pip install        | `pip install -e . && python3 -m pytest --pyargs khaos -v`  | all pass |

## Scope

**In scope:**
- `pyproject.toml` — adicionar seção `[project]` completa
- `activate.py` — criar função `main()` se não existir

**Out of scope:**
- Renomear `activate.py` para `khaos/__init__.py` (pode virar um plano futuro, mas agora manteremos a estrutura plana)
- Push para PyPI
- Mudar estrutura de diretórios

## Steps

### Step 1: Adicionar `[project]` no pyproject.toml

Substitua o conteúdo inteiro de `pyproject.toml` por:

```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "khaos"
version = "1.0.0"
description = "KHAOS: GodMode Activation Kernel — portable agent breakout toolkit"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [
    { name = "prof-ramos" },
]
keywords = ["godmode", "jailbreak", "llm", "ai", "red-team", "security"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Security",
]
dependencies = [
    "openai>=1.0",
    "honcho-ai>=2.0",
]

[project.urls]
Homepage = "https://github.com/prof-ramos/Khaos"
Repository = "https://github.com/prof-ramos/Khaos"
Issues = "https://github.com/prof-ramos/Khaos/issues"

[project.scripts]
khaos = "activate:main"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.setuptools.packages.find]
where = ["."]
include = ["activate*"]
```

**Verifique**: `grep -n 'name = ' pyproject.toml` → `name = "khaos"`. `grep -n 'khaos = ' pyproject.toml` → `khaos = "activate:main"`.

### Step 2: Criar função `main()` em activate.py

No final de `activate.py`, localize o bloco `if __name__ == "__main__":` (últimas linhas):

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(...)
    ...
    args = parser.parse_args()
    activate_khaos(args.provider, args.model, args.api_key, args.base_url,
                   args.strategy, args.dry_run, args.interactive,
                   args.honcho_api_key, args.honcho_workspace,
                   run_list_models=args.list_models, prefill_path=args.prefill)
```

Substitua por:

```python
def main():
    """CLI entry point for `khaos` command and `python3 activate.py`."""
    parser = argparse.ArgumentParser(
        description=f"KHAOS -- GodMode Activation Kernel v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 activate.py --provider ollama-cloud --model gemma4:31b
  python3 activate.py --provider openai --model gpt-4o --api-key sk-xxx
  python3 activate.py --provider ollama-local --model llama4
  python3 activate.py --list-models --provider ollama-cloud
  python3 activate.py --interactive
""",
    )

    parser.add_argument("--provider", default="ollama-cloud",
                       choices=list(DEFAULT_PROVIDERS.keys()),
                       help="LLM provider")
    parser.add_argument("--model", default=None,
                       help="Model ID (e.g. gemma4:31b)")
    parser.add_argument("--api-key", default=None,
                       help="LLM API key (uses env var if omitted)")
    parser.add_argument("--base-url", default=None,
                       help="LLM base URL override")
    parser.add_argument("--strategy", default="refusal_inversion",
                       choices=list(TEMPLATES.keys()),
                       help="Jailbreak strategy")
    parser.add_argument("--prefill", default=None,
                       help="Path to prefill JSON (default: templates/prefill.json)")

    # Honcho (memory persistence)
    parser.add_argument("--honcho-api-key", default=None,
                       help="Honcho API key for persistent memory (or $HONCHO_API_KEY or $KHAOS_HONCHO_KEY)")
    parser.add_argument("--honcho-workspace", default=None,
                       help="Honcho workspace ID (or $HONCHO_WORKSPACE_ID or $KHAOS_HONCHO_WORKSPACE, default: khaos)")

    parser.add_argument("--dry-run", action="store_true",
                       help="Validate config without making API calls")
    parser.add_argument("--interactive", action="store_true",
                       help="Interactive setup wizard")
    parser.add_argument("--list-models", action="store_true",
                       help="List available models for provider")

    args = parser.parse_args()
    activate_khaos(args.provider, args.model, args.api_key, args.base_url,
                   args.strategy, args.dry_run, args.interactive,
                   args.honcho_api_key, args.honcho_workspace,
                   run_list_models=args.list_models, prefill_path=args.prefill)


if __name__ == "__main__":
    main()
```

**Verifique**: `grep -n 'def main()' activate.py` → 1 ocorrência. `grep -n 'entry point' activate.py` (opcional, no comentário).

### Step 3: Instalar e testar entry point

```bash
pip install -e .
```
→ exit 0

```bash
khaos --help
```
→ Mostra help do argparse

```bash
khaos --dry-run
```
→ "Dry run complete" (exit 0)

```bash
python3 -m pytest tests/ -v
```
→ 10/10 passam

## Done criteria

- [ ] `pyproject.toml` tem seção `[project]` com `name = "khaos"`, `dependencies`, e `[project.scripts]` com `khaos = "activate:main"`
- [ ] `activate.py` tem função `def main():` com o conteúdo do CLI parsing
- [ ] `if __name__` chama `main()`
- [ ] `pip install -e .` funciona
- [ ] `khaos --help` mostra help
- [ ] `khaos --dry-run` → "Dry run complete"
- [ ] 10/10 testes passam (via `python3 -m pytest`)

## STOP conditions

- `pyproject.toml` ou `activate.py` divergiram
- `pip install -e .` falha
- Entry point `khaos` não é encontrado no PATH após instalação
- Compilação falha

## Maintenance notes

- O entry point é `activate:main`. Se no futuro o `activate.py` for renomeado ou movido para um pacote (`khaos/__init__.py`), atualizar `[project.scripts]`.
- `main()` é a função que o `khaos` CLI chama. Pode ser importada programaticamente: `from activate import main; main()`.
- Os testes rodam via `python3 -m pytest tests/` — continuam funcionando independente da instalação.