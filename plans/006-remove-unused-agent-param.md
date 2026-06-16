# Plan 006: Remover parâmetro `agent` não utilizado de `honcho_get_context`

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise.
>
> **Drift check**: `git diff --stat ab25f4e..HEAD -- activate.py`
> Se o arquivo mudou, compare os trechos em "Current state" antes de prosseguir.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: Plan 004 (para garantir que except: já foi substituído — mas não é bloqueante)
- **Category**: tech-debt
- **Planned at**: commit `ab25f4e`, 2026-06-15
- **Issue**: https://github.com/prof-ramos/Khaos/issues/6

## Why this matters

O parâmetro `agent` é recebido mas nunca usado no corpo da função. Isso é código enganoso: sugere uma funcionalidade de filtragem que não existe, e qualquer manutenção futura pode assumir incorretamente que o parâmetro é funcional. Removê-lo limpa a API pública.

## Current state

**Definição da função** (linha ~249):
```python
def honcho_get_context(honcho, session, agent):
    """Get conversation context from Honcho."""
    if not honcho or not session:
        return None
    try:
        return session.context(tokens=4000)
    except:
        return None
```

**Chamada** (linha ~551):
```python
ctx = honcho_get_context(honcho, session, agent_peer)
```

O parâmetro `agent` (3º) é recebido em `agent` mas nunca referenciado no corpo.

Convenção do repositório: docstrings curtas em funções utilitárias, sem type hints.

## Commands you will need

| Purpose                      | Command                                                    | Expected on success |
|------------------------------|------------------------------------------------------------|---------------------|
| Compile check                | `python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"` | OK |
| Verify signature             | `grep -n 'def honcho_get_context' activate.py`             | mostra `def honcho_get_context(honcho, session):` |
| Verify call                  | `grep -n 'honcho_get_context(' activate.py`               | mostra `honcho_get_context(honcho, session)` |
| Dry run                      | `python3 activate.py --dry-run`                            | "Dry run complete" |
| Tests                        | `python3 -m pytest tests/ -v`                              | all pass |

## Scope

**In scope:**
- `activate.py` — apenas assinatura e chamada de `honcho_get_context`

**Out of scope:**
- Outras funções Honcho
- Docstring (atualizar se quiser, mas não obrigatório)
- Qualquer outra alteração

## Steps

### Step 1: Alterar a definição da função

Troque:
```python
def honcho_get_context(honcho, session, agent):
```
por:
```python
def honcho_get_context(honcho, session):
```

**Verifique**: `grep -n 'def honcho_get_context' activate.py` → mostra `def honcho_get_context(honcho, session):`

### Step 2: Alterar a chamada

Troque:
```python
ctx = honcho_get_context(honcho, session, agent_peer)
```
por:
```python
ctx = honcho_get_context(honcho, session)
```

**Verifique**: `grep -n 'honcho_get_context(' activate.py` → mostra `(...honcho, session)` sem o 3º argumento

### Step 3: Verificar que `agent_peer` ainda é usado em outros lugares

```bash
grep -n 'agent_peer' activate.py
```
→ Deve aparecer em `run_query_loop()` e na chamada de `honcho_initialize_workspace()`. A variável ainda existe — só não é mais passada para `honcho_get_context`.

### Step 4: Compilar e testar

```bash
python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"
```
→ `OK`

```bash
python3 activate.py --dry-run
```
→ "Dry run complete"

```bash
python3 -m pytest tests/ -v
```
→ 10/10 passam

## Done criteria

- [ ] Assinatura: `def honcho_get_context(honcho, session):`
- [ ] Chamada: `honcho_get_context(honcho, session)`
- [ ] `grep -n '\bagent\b' activate.py | head -5` → `agent_peer` ainda existe em outros lugares
- [ ] Compilação OK
- [ ] Dry run OK
- [ ] 10/10 testes passam

## STOP conditions

- Arquivo divergiu do "Current state"
- Compilação falha
- `agent_peer` some do código (não pode — é usado em `run_query_loop`)