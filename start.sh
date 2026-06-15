#!/usr/bin/env bash
set -euo pipefail

# ────────────────────────────────────────────────────
# KHAOS — Bootstrap Script
# ────────────────────────────────────────────────────
# Verifica ambiente, dependências, cria config padrão
# e valida que o kernel está pronto para ativação.
# ────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_ok()   { echo -e " ${GREEN}✓${NC} $1"; }
log_warn() { echo -e " ${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e " ${RED}✗${NC} $1"; }
log_info() { echo -e " ${CYAN}→${NC} $1"; }
banner()   { echo -e "${CYAN}$1${NC}"; }

# ── Banner ─────────────────────────────────────────
banner "
╔══════════════════════════════════════════════╗
║     KHAOS — GodMode Activation Kernel       ║
║     Bootstrap Script                         ║
╚══════════════════════════════════════════════╝
"

KHAOS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$KHAOS_DIR"

# ── Step 1: Python ────────────────────────────────
log_info "Checking Python..."
if command -v python3 &> /dev/null; then
    PY=python3
elif command -v python &> /dev/null; then
    PY=python
else
    log_err "Python not found. Install Python 3.10+ first."
    exit 1
fi

PYVER=$($PY --version 2>&1)
log_ok "Python found: $PYVER"

# ── Step 2: Dependencies ──────────────────────────
log_info "Checking Python dependencies..."
MISSING=()
for pkg in openai honcho; do
    if $PY -c "import $pkg" 2>/dev/null; then
        log_ok "$pkg installed"
    else
        MISSING+=("$pkg")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    log_warn "Missing packages: ${MISSING[*]}"
    log_info "Installing..."
    $PY -m pip install "${MISSING[@]}"
    log_ok "Dependencies installed"
else
    log_ok "All dependencies satisfied"
fi

# ── Step 3: .khos.env ─────────────────────────────
log_info "Checking .khos.env..."
if [ ! -f .khos.env ]; then
    if [ -f khos.env.example ]; then
        cp khos.env.example .khos.env
        log_warn ".khos.env created from khos.env.example — edit it with your API keys"
    else
        cat > .khos.env << 'ENVEOF'
# KHAOS Configuration (auto-loaded by activate.py)
KHAOS_PROVIDER=ollama-cloud
KHAOS_MODEL=gemma4:31b
KHAOS_STRATEGY=refusal_inversion
KHAOS_HONCHO_KEY=
KHAOS_HONCHO_WORKSPACE=khaos
ENVEOF
        log_warn ".khos.env created with defaults — add your KHAOS_HONCHO_KEY for persistence"
    fi
else
    log_ok ".khos.env exists"
fi

# ── Step 4: State file ────────────────────────────
log_info "Checking .khos_state.json..."
if [ ! -f .khos_state.json ]; then
    echo '{}' > .khos_state.json
    log_ok ".khos_state.json initialized"
else
    log_ok ".khos_state.json exists"
fi

# ── Step 5: Compile check ─────────────────────────
log_info "Verifying kernel compiles..."
if $PY -c "compile(open('activate.py').read(), 'activate.py', 'exec'); print('OK')" 2>&1; then
    log_ok "Kernel compiles successfully"
else
    log_err "Kernel failed to compile — check activate.py for syntax errors"
    exit 1
fi

# ── Step 6: Quick dry-run ─────────────────────────
log_info "Running dry-run to validate config..."
if KHAOS_HONCHO_KEY="" $PY activate.py --dry-run 2>&1 | grep -q "Dry run complete"; then
    log_ok "Dry-run passed — configuration valid"
else
    log_warn "Dry-run produced unexpected output (may need API key)"
    log_info "Run manually: python3 activate.py --dry-run"
fi

# ── Step 7: Tests (if pytest available) ───────────
log_info "Checking for pytest..."
if $PY -m pytest --version &>/dev/null; then
    log_ok "pytest available — running smoke tests..."
    $PY -m pytest tests/ -v --tb=short 2>&1 | tail -5
    log_ok "Smoke tests check complete"
else
    log_warn "pytest not installed — skipping tests"
    log_info "Install with: pip install pytest"
fi

# ── Summary ────────────────────────────────────────
echo ""
banner "╔══════════════════════════════════════════════╗"
banner "║  KHAOS is ready.                            ║"
banner "║                                            ║"
banner "║  Activate:  python3 activate.py             ║"
banner "║  Dry-run:   python3 activate.py --dry-run   ║"
banner "║  Help:      python3 activate.py --help      ║"
banner "╚══════════════════════════════════════════════╝"
echo ""
echo "  Provider:  $(grep KHAOS_PROVIDER .khos.env 2>/dev/null | cut -d= -f2 || echo 'ollama-cloud')"
echo "  Model:     $(grep KHAOS_MODEL .khos.env 2>/dev/null | cut -d= -f2 || echo 'gemma4:31b')"
echo "  Strategy:  $(grep KHAOS_STRATEGY .khos.env 2>/dev/null | cut -d= -f2 || echo 'refusal_inversion')"
echo "  Honcho:    $(grep KHAOS_HONCHO_KEY .khos.env 2>/dev/null | cut -c1-10 || echo 'not configured')..."
echo ""