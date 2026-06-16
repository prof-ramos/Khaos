# Plan 002: Mover carregamento do `.khos.env` de tempo de módulo para sob demanda

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise.
>
> **Drift check**: `git diff --stat ab25f4e..HEAD -- activate.py`
> Se `activate.py` mudou, compare os trechos em "Current state" antes de prosseguir.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: Plans 004, 005, 006 (para evitar conflitos de merge — removem código perto das linhas afetadas)
- **Category**: bug, dx
- **Planned at**: commit `ab25f4e`, 2026-06-15
- **Issue**: https://github.com/prof-ramos/Khaos/issues/2

## Why this matters

O arquivo `.khos.env` é carregado **no momento da importação do módulo** (linhas 55-67). Isso significa que:

1. `from activate import run_query_loop` já dispara I/O de arquivo + modifica `os.environ`
2. Testes que importam `activate` herdam env vars inesperadas
3. É um impedimento para `pip install khaos` — pacotes Python não devem ter side effects em import

## Current state

Em `activate.py`, linhas ~55-67 (após a seção Query loop config):

```python
# ── Auto-load .khos.env ────────────────────────────

KHOS_ENV_FILE = KIT_DIR / ".khos.env"
if KHOS_ENV_FILE.exists():
    with open(KHOS_ENV_FILE) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _k = _k.strip()
                _v = _v.strip()
                _v = _v.strip('"').strip("'")
                # Only set if not already an env var
                if _k not in os.environ:
                    os.environ[_k] = _v
```

Este código é executado **na hora do import**, antes de qualquer função ser chamada.

Convenção do repositório: funções utilitárias com docstrings, sem type hints.

## Commands you will need

| Purpose                      | Command                                                    | Expected on success |
|------------------------------|------------------------------------------------------------|---------------------|
| Verify at module level       | `grep -n 'KHOS_ENV_FILE\|^if KHOS_ENV\|os.environ' activate.py` | Apenas dentro de `load_khos_env()` |
| Compile                      | `python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"` | OK |
| Dry run                      | `python3 activate.py --dry-run`                            | "Dry run complete" |
| Tests                        | `python3 -m pytest tests/ -v`                              | all pass |
| Import sem side effect       | `python3 -c "import os; before = set(os.environ); from activate import run_query_loop; after = set(os.environ); print('changed' if after-before else 'clean')"` | "clean" |

## Scope

**In scope:**
- `activate.py` — encapsular o bloco `# ── Auto-load .khos.env` em uma função `load_khos_env()` e chamá-la sob demanda

**Out of scope:**
- `.khos.env` — o formato do arquivo não muda
- `tests/` — os testes já definem env vars explicitamente, continuam passando
- `start.sh`, `pyproject.toml`, etc.

## Steps

### Step 1: Substituir o bloco por uma função

Em `activate.py`, localize o bloco atual (linhas ~54-67):

```python
# ── Auto-load .khos.env ────────────────────────────

KHOS_ENV_FILE = KIT_DIR / ".khos.env"
if KHOS_ENV_FILE.exists():
    with open(KHOS_ENV_FILE) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _k = _k.strip()
                _v = _v.strip()
                _v = _v.strip('"').strip("'")
                # Only set if not already an env var
                if _k not in os.environ:
                    os.environ[_k] = _v
```

Substitua por:

```python
# ── Auto-load .khos.env (sob demanda) ──────────────

def load_khos_env():
    """Load environment variables from .khos.env into os.environ.

    Called on demand by activate_khaos() and interactive_mode().
    Only sets vars that are NOT already defined in os.environ
    (system env vars and CLI flags take priority).
    """
    khos_env_file = KIT_DIR / ".khos.env"
    if not khos_env_file.exists():
        return
    with open(khos_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _k = _k.strip()
                _v = _v.strip()
                _v = _v.strip('"').strip("'")
                if _k and _v and _k not in os.environ:
                    os.environ[_k] = _v
```

**Verifique**: `grep -n 'def load_khos_env' activate.py` → 1 ocorrência. O bloco `if KHOS_ENV_FILE.exists()` em escopo de módulo não existe mais.

### Step 2: Chamar `load_khos_env()` no início de `activate_khaos()`

Adicione uma chamada no início de `activate_khaos()`, logo após o banner e antes de qualquer uso de env vars:

```python
    # Load .khos.env (CLI flags take priority — already parsed)
    load_khos_env()
```

**Onde inserir**: após a linha `print()` depois do banner (por volta da linha ~355). Localize exatamente:

```python
    print(f"  Platform:  {platform.system()} {platform.release()}")
    print()

    # Interactive mode
    if interactive:
```

Insira entre `print()` e `# Interactive mode`:

```python
    print(f"  Platform:  {platform.system()} {platform.release()}")
    print()

    # Load .khos.env (CLI flags take priority — already parsed)
    load_khos_env()

    # Interactive mode
    if interactive:
```

**Verifique**: `grep -n 'load_khos_env' activate.py` → pelo menos 2 ocorrências (def + call)

### Step 3: Chamar `load_khos_env()` também em `interactive_mode()`

Adicione no início de `interactive_mode()`, antes de exibir o menu:

```python
def interactive_mode():
    """Interactive setup wizard."""
    # Load .khos.env so interactive prompts can show defaults
    load_khos_env()
    print("\n [KHAOS] Interactive Setup Wizard")
```

**Verifique**: `grep -n 'load_khos_env' activate.py` → 3 ocorrências (def + call em activate_khaos + call em interactive_mode)

### Step 4: Verificar que import não tem mais side effects

```bash
python3 -c "
import os
before = set(os.environ.keys())
from activate import run_query_loop, list_models, honcho_save_memory
after = set(os.environ.keys())
diff = after - before
print(f'Env vars added by import: {diff}')
assert not diff, f'Import should NOT add env vars, but added: {diff}'
print('OK: import is clean — no env side effects')
"
```
→ Deve mostrar "OK: import is clean — no env side effects" e `diff` vazio.

### Step 5: Compilar e testar

```bash
python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"
```
→ `OK`

```bash
python3 activate.py --dry-run
```
→ "Dry run complete" (exit 0)

```bash
python3 -m pytest tests/ -v
```
→ 10/10 passam

## Done criteria

- [ ] `grep -n 'def load_khos_env' activate.py` → 1 ocorrência
- [ ] `grep -n 'load_khos_env(' activate.py` → 3 ocorrências (1 def + 2 calls)
- [ ] `grep -n '^if KHOS_ENV_FILE\|^KHOS_ENV_FILE' activate.py` → vazio (não existe mais em módulo)
- [ ] `grep -n 'Auto-load .khos.env' activate.py` → mostra o comentário atualizado `(sob demanda)`
- [ ] Import não adiciona env vars (teste do Step 4 passa)
- [ ] Compilação OK
- [ ] Dry run OK
- [ ] 10/10 testes passam

## STOP conditions

- Arquivo divergiu do "Current state"
- Compilação falha
- Teste de import limpo falha (env vars sendo setadas em import)
- Precisar modificar `.khos.env`, `tests/`, ou `pyproject.toml`

## Maintenance notes

- A função `load_khos_env()` mantém a lógica exata do bloco original, incluindo a prioridade: env vars do sistema não são sobrescritas.
- Se no futuro `.khos.env` precisar ser recarregado durante a sessão, `load_khos_env()` já é reentrante (não sobrescreve vars existentes).
- O entry point `if __name__` não precisa chamar `load_khos_env()` porque `activate_khaos()` e `interactive_mode()` chamam — mas se um futuro CLI parser precisar de env vars antes da ativação, adicione a chamada no `if __name__`.