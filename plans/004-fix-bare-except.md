# Plan 004: Substituir `except:` nus por exceções nomeadas

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat ab25f4e..HEAD -- activate.py`
> Se `activate.py` mudou desde que o plano foi escrito, compare os trechos
> em "Current state" contra o código atual antes de prosseguir. Se divergir,
> STOP.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Planned at**: commit `ab25f4e`, 2026-06-15
- **Issue**: https://github.com/prof-ramos/Khaos/issues/4

## Why this matters

`except:` sem especificar a exceção captura **tudo**, inclusive `KeyboardInterrupt` e `SystemExit`. Isso significa que Ctrl+C pode ser engolido silenciosamente em pontos específicos, e bugs reais podem sumir sem rastro. Trocar por exceções nomeadas mantém a funcionalidade pretendida sem os efeitos colaterais.

## Current state

Duas ocorrências de `except:` nu em `activate.py`:

**1. `honcho_get_context()` — linha ~255:**
```python
    try:
        return session.context(tokens=4000)
    except:
        return None
```

**2. `interactive_mode()` — linha ~615:**
```python
    try:
        provider = providers[int(choice) - 1]
    except:
        provider = "ollama-cloud"
```

Convenção do repositório: Python padrão, sem type hints, variáveis no escopo da função. O código usa `except Exception as e:` nas demais funções (veja linhas 189, 230, 245, 495, 575, 599 como exemplos a seguir).

## Commands you will need

| Purpose                      | Command                                                    | Expected on success |
|------------------------------|------------------------------------------------------------|---------------------|
| Compile check                | `python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"` | OK |
| Verify no bare except        | `grep -n '\bexcept\s*:' activate.py`                      | vazio (exit 1) |
| Dry run                      | `python3 activate.py --dry-run`                            | "Dry run complete" |
| Tests                        | `python3 -m pytest tests/ -v`                              | all pass |

## Scope

**In scope:**
- `activate.py` — apenas as 2 linhas com `except:`

**Out of scope:**
- Qualquer outra mudança em `activate.py`
- `templates/`, `tests/`, `SOUL.md`, `pyproject.toml`

## Git workflow

- Branch: `main` (push direto)
- Commit message: `fix: replace bare except: with named exceptions`
- Do NOT push — o operador fará o push

## Steps

### Step 1: Substituir `except:` por `except Exception:` em `honcho_get_context()`

Em `activate.py`, localize:
```python
    except:
        return None
```
(dentro de `honcho_get_context()`, linha ~255)

Substitua por:
```python
    except Exception:
        return None
```

**Verifique**: `grep -n 'except:' activate.py` → linha ~255 deve mostrar `except Exception:` em vez de `except:`

### Step 2: Substituir `except:` por `except (IndexError, ValueError):` em `interactive_mode()`

Em `activate.py`, localize:
```python
    except:
        provider = "ollama-cloud"
```
(dentro de `interactive_mode()`, linha ~615)

Substitua por:
```python
    except (IndexError, ValueError):
        provider = "ollama-cloud"
```

**Verifique**: `grep -n 'except:' activate.py` → linha ~615 deve mostrar `except (IndexError, ValueError):` em vez de `except:`

### Step 3: Verificar que não sobrou nenhum `except:` nu

```bash
grep -n '\bexcept\s*:' activate.py
```
→ Deve retornar vazio (exit code 1). Todos os `except:` agora têm exceção nomeada.

### Step 4: Compilar e testar

```bash
python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"
```
→ `OK`

```bash
python3 activate.py --dry-run
```
→ Saída contém "Dry run complete" (exit 0)

```bash
python3 -m pytest tests/ -v
```
→ Todos os 10 testes passam

## Done criteria

- [ ] `grep -n '\bexcept\s*:' activate.py` retorna vazio (nenhum except nu)
- [ ] Compilação passa: `python3 -c "compile(...)"` → OK
- [ ] Dry-run passa: "Dry run complete"
- [ ] Todos os 10 testes passam

## STOP conditions

- O código em "Current state" não corresponde ao arquivo atual (drift)
- Compilação Python falha após qualquer passo
- Precisar modificar arquivos fora do escopo

## Maintenance notes

- A convenção do repositório é `except Exception as e:` (com `as e`). Se no futuro um erro precisar ser logado, adicione ` as e` e um `print()`.
- `except (IndexError, ValueError):` em `interactive_mode()` cobre os casos de input inválido. Se o bloco crescer, reavaliar.