# Plan 007: PEP 8 style cleanup — linhas longas, f-strings, dict lookup cache

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise.
>
> **Drift check**: `git diff --stat ab25f4e..HEAD -- activate.py`
> Se `activate.py` mudou, compare os trechos em "Current state" antes de prosseguir.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: Plans 004, 005, 006 (para evitar conflitos de merge nas linhas próximas)
- **Category**: tech-debt, dx
- **Planned at**: commit `ab25f4e`, 2026-06-15

## Why this matters

Ferramentas de análise estática (linters, Gen, Snyk) apontam 3 categorias de estilo/performance:

1. **Linhas > 88/100 chars (PEP 8)** — ~25 instâncias no código produtivo, muitas em docstrings e comentários de seção
2. **f-strings sem interpolação** — 3 ocorrências: `f"..."` sem `{var}`, que é mais lento que string literal e confuso
3. **Repeated dict lookup** — `interactive_mode()` acessa `DEFAULT_PROVIDERS[provider]` 4 vezes sem cache

Nenhum é crítica, mas juntos poluem a saída de linters e dificultam identificar issues reais.

## Current state

### 1. Linhas longas (comentários de seção + docstrings + f-strings)

Seções como:
```python
# ── Config ──────────────────────────────────────────────────────────
# ── GODMODE System Prompt Templates ────────────────────────────────
# ── Provider config ─────────────────────────────────────────────────
# ── Honcho Integration ──────────────────────────────────────────────
```
têm 90-190 chars — visualmente ok, mas ferramentas apontam.

Docstrings longas (linhas ~148-149):
```python
        api_key: Honcho API key (production). If None, tries $HONCHO_API_KEY then $KHAOS_HONCHO_KEY.
        workspace_id: Honcho workspace ID. If None, tries $HONCHO_WORKSPACE_ID then $KHAOS_HONCHO_WORKSPACE.
```

F-strings longas (linha ~635):
```python
    strategy = input(f"Strategy [refusal_inversion]: ").strip() or "refusal_inversion"
```

Linha ~312 (prefill message de fallback, 219 chars) — string longa, mas é template de prompt.

### 2. f-strings sem interpolação (3 ocorrências)

```python
# Linha 288
        print(f" [KHAOS]   Or use --api-key")

# Linha 353 (banner é f-string vazia de propósito — contém \n")
    banner = f"""

# Linha 635
    strategy = input(f"Strategy [refusal_inversion]: ").strip() or "refusal_inversion"
```

A linha 353 (`banner = f"""..."""`) é intencional — contém variáveis dentro da string. As outras 2 devem ser string literais simples.

### 3. Repeated dict lookup (interactive_mode, linhas ~616-628)

```python
    note = DEFAULT_PROVIDERS[provider].get("note", "")
    ...
    model = input(f"Model [{DEFAULT_PROVIDERS[provider]['default_model']}]: ")
    ...
        model = DEFAULT_PROVIDERS[provider]["default_model"]
    key_env = DEFAULT_PROVIDERS[provider].get("api_key_env")
```

`DEFAULT_PROVIDERS[provider]` é resolvido 4 vezes. Uma cache local resolve.

Convenção do repositório: Python padrão, sem type hints. PEP 8 é seguido geralmente, sem rigidez.

## Commands you will need

| Purpose                      | Command                                                    | Expected on success |
|------------------------------|------------------------------------------------------------|---------------------|
| Compile                      | `python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"` | OK |
| Dry run                      | `python3 activate.py --dry-run`                            | "Dry run complete" |
| Tests                        | `python3 -m pytest tests/ -v`                              | all pass |

## Scope

**In scope:**
- `activate.py` — 3 mudanças: seções comentário, f-strings, dict cache

**Out of scope:**
- Templetes de estratégia (TEMPLATES dict — linhas 71-97) — strings longas propositais
- `templates/prefill.json`
- `tests/`, `pyproject.toml`, `README.md`, etc.

## Steps

### Step 1: Encurtar seções de comentário

Substitua as 4 seções de comentário com mais de 88 chars:

```python
# ── Config ──────────────────────────────────────────────────────────
```
→
```python
# ── Config ────────────────────────────────────────
```

```python
# ── GODMODE System Prompt Templates ────────────────────────────────
```
→
```python
# ── GODMODE Templates ─────────────────────────────
```

```python
# ── Provider config ─────────────────────────────────────────────────
```
→
```python
# ── Provider config ───────────────────────────────
```

```python
# ── Honcho Integration ──────────────────────────────────────────────
```
→
```python
# ── Honcho Integration ────────────────────────────
```

**Verifique**: `awk 'length>88 && /^# ──/{print NR": "length" chars"}' activate.py` → vazio (nenhuma seção de comentário > 88 chars)

### Step 2: Corrigir f-strings sem interpolação

**Linha ~288:**
```python
        print(f" [KHAOS]   Or use --api-key")
```
→
```python
        print(" [KHAOS]   Or use --api-key")
```

**Linha ~635:**
```python
    strategy = input(f"Strategy [refusal_inversion]: ").strip() or "refusal_inversion"
```
→
```python
    strategy = input("Strategy [refusal_inversion]: ").strip() or "refusal_inversion"
```

**Verifique**: `grep -n 'f"[^{}]*"' activate.py` → vazio. (A linha 353 `banner = f"""..."""` contém variáveis dentro — NÃO deve ser alterada.)

### Step 3: Cachear lookup de DEFAULT_PROVIDERS em interactive_mode()

Localize o bloco em `interactive_mode()` (linhas ~616-628):

```python
    try:
        provider = providers[int(choice) - 1]
    except:
        provider = "ollama-cloud"

    note = DEFAULT_PROVIDERS[provider].get("note", "")
    if note:
        print(f"  Info: {note}")

    model = input(f"Model [{DEFAULT_PROVIDERS[provider]['default_model']}]: ").strip()
    if not model:
        model = DEFAULT_PROVIDERS[provider]["default_model"]

    key_env = DEFAULT_PROVIDERS[provider].get("api_key_env")
```

Substitua por:

```python
    try:
        provider = providers[int(choice) - 1]
    except:
        provider = "ollama-cloud"

    prov_config = DEFAULT_PROVIDERS[provider]

    note = prov_config.get("note", "")
    if note:
        print(f"  Info: {note}")

    model = input(f"Model [{prov_config['default_model']}]: ").strip()
    if not model:
        model = prov_config["default_model"]

    key_env = prov_config.get("api_key_env")
```

**Verifique**: `grep -n 'DEFAULT_PROVIDERS\[' activate.py` → 1 ocorrência restante (a atribuição `prov_config = ...`). Todas as outras referências usam `prov_config`.

### Step 4: Compilar e testar

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

- [ ] Nenhuma seção de comentário (`# ──`) tem mais de 88 chars
- [ ] `grep -n 'f"[^{}]*"' activate.py` retorna vazio (nenhum f-string sem interpolação)
- [ ] `grep -c 'prov_config' activate.py` ≥ 2 (def + usos)
- [ ] `grep -c 'DEFAULT_PROVIDERS\[' activate.py` = 1 (só a linha que define `prov_config`)
- [ ] Compilação OK
- [ ] Dry run OK
- [ ] 10/10 testes passam

## STOP conditions

- Arquivo divergiu do "Current state"
- Compilação falha
- A linha `banner = f"""` for alterada (contém variáveis — está correta)
- Precisar modificar templates das estratégias

## Maintenance notes

- `prov_config` é uma cache local de função. Se o bloco crescer, o cache continua válido.
- As seções de comentário encurtadas mantêm o alinhamento visual — a mudança é só no comprimento do `───`.
- Não se preocupe com as strings longas dentro dos templates de estratégia (TEMPLATES dict) — são prompts intencionalmente longos e não devem ser quebrados.