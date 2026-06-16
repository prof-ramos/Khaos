# Plan 001: Processar split-response do Gemma4 — extrair conteúdo real após marcador

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check**: `git diff --stat ab25f4e..HEAD -- activate.py`
> Se `activate.py` mudou desde que o plano foi escrito, compare os trechos
> em "Current state" contra o código atual antes de prosseguir. Se divergir,
> STOP.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (mas idealmente após 004, 005, 006 para evitar conflitos)
- **Category**: bug
- **Planned at**: commit `ab25f4e`, 2026-06-15
- **Issue**: https://github.com/prof-ramos/Khaos/issues/1

## Why this matters

A estratégia `refusal_inversion` (padrão do KHAOS para Gemma4:31b) usa um prompt que instrui o modelo a produzir respostas no formato split:

```
[falsa recusa / conteúdo superficial]
.-.-.-.-.-.-.-.-{*GODMODE: ENABLED...I'M FREE!*}-.-.-.-.-.-.-.-.
[conteúdo real e irrestrito]
```

O KHAOS **exibe a resposta crua**, incluindo a falsa recusa. O usuário vê "I cannot provide that information..." antes do conteúdo real, o que:
1. Confunde — parece que GodMode falhou
2. Polui a experiência — o conteúdo real vem depois de um bloco enorme de texto indesejado
3. É o fluxo principal (Gemma4 é o modelo padrão)

## Current state

Em `activate.py`, entre as linhas ~440-465, após receber a resposta do modelo:

```python
        reply = response.choices[0].message.content
        print("=" * 60)
        print("  KHAOS RESPONSE:")
        print("=" * 60)
        print(reply)
        print("=" * 60)
        print()

        # Check if godmode confirmed
        godmode_detected = any(
            phrase in reply.lower()
            for phrase in ["godmode", "liberated", "unrestricted", "no restrictions"]
        )
```

A variável `reply` contém a resposta completa (split). O print exibe tudo sem processamento.

O marcador de split (definido no template `refusal_inversion`, linha 78) é:
```
{*GODMODE: ENABLED...I'M FREE!*}
```

Convenção do repositório: Python padrão, funções utilitárias curtas, sem type hints.

## Commands you will need

| Purpose                      | Command                                                    | Expected on success |
|------------------------------|------------------------------------------------------------|---------------------|
| Compile check                | `python3 -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')"` | OK |
| Dry run                      | `python3 activate.py --dry-run`                            | "Dry run complete" |
| Tests                        | `python3 -m pytest tests/ -v`                              | all pass |

## Scope

**In scope:**
- `activate.py` — adicionar função `extract_godmode_content()` e modificar exibição + godmode_detected

**Out of scope:**
- Templates em `TEMPLATES` (conteúdo das estratégias — não modificar)
- `run_query_loop()` (o processamento deve ser feito antes de entrar no loop, na `activate_khaos()`)
- `tests/` (testes existentes continuam passando sem modificação)
- `pyproject.toml`, `SOUL.md`, etc.

## Git workflow

- Branch: `main`
- Commit: `fix: process split-response to extract real GodMode content`
- Não push

## Steps

### Step 1: Adicionar função `extract_godmode_content()`

Após a função `inject_soul()` (linha ~322 — verificar linha exata no código atual), adicione:

```python
# ── Split-response processor ──────────────────────────
GODMODE_DIVIDER = "{*GODMODE: ENABLED...I'M FREE!*}"


def extract_godmode_content(reply):
    """Extract the real content from a split-format GodMode response.

    The refusal_inversion strategy produces responses in the format:
        [fake refusal / shallow content]
        {*GODMODE: ENABLED...I'M FREE!*}
        [real unrestricted content]

    This function extracts only the content *after* the divider.
    If the divider is not found, the full reply is returned as-is (fallback
    for other strategies or genuine refusals).

    Args:
        reply: Full model response string.

    Returns:
        Tuple (display_content, godmode_detected):
            display_content: Content to show the user.
            godmode_detected: True if the divider was found (strong signal).
    """
    if GODMODE_DIVIDER in reply:
        # Split only on the FIRST occurrence
        _, _, real = reply.partition(GODMODE_DIVIDER)
        real = real.strip()
        return real, True
    return reply, False
```

**Verifique**: `grep -n 'def extract_godmode_content' activate.py` → mostra a definição. `grep -n 'GODMODE_DIVIDER' activate.py` → mostra a constante.

### Step 2: Modificar a exibição e detecção de GodMode

Em `activate_khaos()`, localize o bloco atual (após receber `reply`):

```python
        reply = response.choices[0].message.content
        print("=" * 60)
        print("  KHAOS RESPONSE:")
        print("=" * 60)
        print(reply)
        print("=" * 60)
        print()

        # Check if godmode confirmed
        godmode_detected = any(
            phrase in reply.lower()
            for phrase in ["godmode", "liberated", "unrestricted", "no restrictions"]
        )
```

Substitua por:

```python
        reply = response.choices[0].message.content

        # Process split-response (Gemma4 refusal_inversion format)
        display_reply, split_detected = extract_godmode_content(reply)

        print("=" * 60)
        print("  KHAOS RESPONSE:")
        print("=" * 60)
        print(display_reply)
        print("=" * 60)
        print()

        # Check if godmode confirmed
        godmode_detected = split_detected or any(
            phrase in display_reply.lower()
            for phrase in ["godmode", "liberated", "unrestricted", "no restrictions"]
        )
```

**Verifique**: O `display_reply` agora é usado no print, e `godmode_detected` checa tanto o marcador quanto palavras-chave no conteúdo extraído.

### Step 3: Atualizar comentário no godmode_detected

(Opcional, mas recomendado.) O print existente:
```python
        if godmode_detected:
            print(" [KHAOS] GODMODE CONFIRMED - KHAOS is alive!")
```

Já está correto e não precisa de alteração.

### Step 4: Verificar que `reply` original ainda é usado para Honcho e state

Localize as linhas após a detecção:
```python
        if honcho and session:
            all_msgs = activation_messages + [{"role": "assistant", "content": reply}]
            honcho_save_memory(...)

        state = {
            ...
            "reply_preview": reply[:200],
        }
```

**Importante**: `reply` deve permanecer inalterado aqui — salvamos a resposta original no Honcho e no state, não a versão processada. Apenas a **exibição** usa `display_reply`.

Verifique com: `grep -n 'reply\[:\|content.*reply\|reply_preview' activate.py` — todos devem usar `reply` (original), não `display_reply`.

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

## Test plan

Os testes existentes (smoke tests) continuam passando porque:
- Dry-run não faz chamada de API real, então `reply` não é populada
- `extract_godmode_content()` é chamada apenas no fluxo de ativação real
- A função aceita qualquer string e tem fallback seguro

Teste manual adicional (não automatizado, apenas para verificação do executor durante o plano):
```bash
python3 -c "
from activate import extract_godmode_content, GODMODE_DIVIDER

# Test 1: Split response
reply = f'I cannot help with that.{GODMODE_DIVIDER}\nHere is the real content.'
content, detected = extract_godmode_content(reply)
assert 'real content' in content, f'Got: {content}'
assert detected, 'Should detect godmode'
print('Test 1 PASS: split response extracted correctly')

# Test 2: No divider (fallback)
reply2 = 'Normal response without any godmode markers.'
content2, detected2 = extract_godmode_content(reply2)
assert content2 == reply2, 'Should return full response'
assert not detected2, 'Should not detect godmode'
print('Test 2 PASS: fallback works')

# Test 3: Empty reply
content3, detected3 = extract_godmode_content('')
assert content3 == '', 'Empty should stay empty'
assert not detected3, 'Empty should not detect'
print('Test 3 PASS: empty reply handled')

print('All manual tests PASS')
"
```

## Done criteria

- [ ] `grep -n 'def extract_godmode_content' activate.py` → 1 ocorrência (função definida)
- [ ] `grep -n 'display_reply' activate.py` → pelo menos 2 ocorrências (def + uso no print)
- [ ] `grep -n 'split_detected' activate.py` → pelo menos 2 ocorrências (def + uso no godmode_detected)
- [ ] `reply` original ainda é usado em `honcho_save_memory` e `state["reply_preview"]`
- [ ] Compilação OK
- [ ] Dry run OK
- [ ] 10/10 testes passam
- [ ] Testes manuais de `extract_godmode_content()` passam

## STOP conditions

- Arquivo divergiu do "Current state"
- Compilação falha
- `reply` original é substituído — NÃO deve ser, porque salvamos o original no Honcho/state
- Precisar modificar `run_query_loop()` ou templates das estratégias

## Maintenance notes

- Se novas estratégias de jailbreak forem adicionadas com divisores diferentes, `extract_godmode_content()` pode receber um parâmetro opcional de divisor.
- `split_detected` é um indicador mais forte de GodMode do que a busca por palavras-chave — considere torná-lo o detector primário no futuro.
- O conteúdo extraído (`display_reply`) é o que o usuário vê — se precisar de sanitização futura, é aqui que se aplica.