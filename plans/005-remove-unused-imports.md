# Plan 005: Remover imports não utilizados (time, subprocess)

> **Executor instructions**: Siga o plano passo a passo. Execute cada comando
> de verificação e confirme o resultado esperado antes de prosseguir. Se
> qualquer condição de STOP ocorrer, pare e reporte — não improvise.
>
> **Drift check**: `git diff --stat ab25f4e..HEAD -- activate.py`
> Se o arquivo mudou, compare os trechos em "Current state" antes de prosseguir.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: tech-debt
- **Planned at**: commit `ab25f4e`, 2026-06-15
- **Issue**: https://github.com/prof-ramos/Khaos/issues/5

## Why this matters

Imports não utilizados poluem o namespace, podem gerar falsos positivos em linters, e atrapalham análise de dependências. Removê-los é limpeza simples de baixo risco.

## Current state

Em `activate.py`, linhas 31-39:

```python
import os
import sys
import json
import time        # ← NUNCA usado (time. nowhere in code)
import argparse
import subprocess  # ← NUNCA usado (subprocess. nowhere in code)
import platform
from datetime import datetime
from pathlib import Path
```

`time` e `subprocess` não aparecem em nenhum lugar do código. `pathlib.Path` é usado (KIT_DIR, STATE_FILE, etc.) e deve permanecer.

Convenção do repositório: imports padrão do Python, um por linha, ordenados alfabeticamente dentro do grupo padrão.

## Commands you will need

| Purpose                      | Command                                                    | Expected on success |
|------------------------------|------------------------------------------------------------|---------------------|
| Verify unused                | `grep -n '\btime\.\b\|subprocess\.' activate.py`           | vazio (exit 1) |
| Compile check                | `python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"` | OK |
| Dry run                      | `python3 activate.py --dry-run`                            | "Dry run complete" |
| Tests                        | `python3 -m pytest tests/ -v`                              | all pass |

## Scope

**In scope:**
- `activate.py` — remover 2 linhas

**Out of scope:**
- Outros imports (os, sys, json, argparse, platform, datetime, pathlib — NÃO remover)
- Qualquer outra alteração

## Git workflow

- Branch: `main` (push direto)
- Commit: `chore: remove unused imports (time, subprocess)`
- Não push — operador fará o push

## Steps

### Step 1: Remover as 2 linhas

Edite `activate.py` removendo:
```python
import time
```
e
```python
import subprocess
```

O bloco deve ficar:
```python
import os
import sys
import json
import argparse
import platform
from datetime import datetime
from pathlib import Path
```

**Verifique**: `grep -n '^import time\|^import subprocess' activate.py` → vazio (exit 1)

### Step 2: Compilar e testar

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

- [ ] `grep -n '^import time\|^import subprocess' activate.py` retorna vazio
- [ ] Compilação OK
- [ ] Dry run OK
- [ ] 10/10 testes passam

## STOP conditions

- Arquivo divergiu do "Current state"
- Compilação falha
- Precisar tocar arquivos fora do escopo