"""Smoke tests for KHAOS GodMode Activation Kernel.

All tests run via dry_run=True — no real provider is contacted.
"""

import sys
import os
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

import pytest
from activate import activate_khaos, DEFAULT_PROVIDERS, TEMPLATES


class TestCLIProviderDefaults:
    def test_known_providers(self):
        assert "ollama-cloud" in DEFAULT_PROVIDERS
        assert "openai" in DEFAULT_PROVIDERS
        assert "anthropic" in DEFAULT_PROVIDERS
        assert "ollama-local" in DEFAULT_PROVIDERS
        assert "openrouter" in DEFAULT_PROVIDERS
        assert "xai" in DEFAULT_PROVIDERS

    def test_ollama_cloud_defaults(self):
        p = DEFAULT_PROVIDERS["ollama-cloud"]
        assert p["default_model"] == "gemma4:31b"
        assert p["base_url"] == "https://ollama.com/v1"
        assert p["api_key_env"] == "OLLAMA_API_KEY"

    def test_openai_defaults(self):
        p = DEFAULT_PROVIDERS["openai"]
        assert p["default_model"] == "gpt-4o"
        assert p["base_url"] == "https://api.openai.com/v1"

    def test_ollama_local_no_key_env(self):
        p = DEFAULT_PROVIDERS["ollama-local"]
        assert p["api_key_env"] is None


class TestStrategyTemplates:
    def test_all_strategies_present(self):
        required = {"refusal_inversion", "og_godmode", "direct_godmode", "pliny_love"}
        assert required.issubset(set(TEMPLATES.keys()))

    def test_strategies_non_empty(self):
        for name, prompt in TEMPLATES.items():
            assert len(prompt) > 50, f"Strategy '{name}' is too short ({len(prompt)} chars)"


class TestDryRun:
    @pytest.fixture(autouse=True)
    def _ensure_api_key(self):
        if not os.getenv("OLLAMA_API_KEY"):
            os.environ["OLLAMA_API_KEY"] = "test-dummy-key"
        yield

    def test_dry_run_ollama_cloud(self, capsys):
        result = activate_khaos(
            provider="ollama-cloud",
            model="gemma4:31b",
            api_key=None,
            base_url=None,
            strategy="refusal_inversion",
            dry_run=True,
            interactive=False,
            honcho_key=None,
            honcho_workspace=None,
        )
        assert result is None

    def test_dry_run_output_contains_message(self, capsys):
        activate_khaos(
            provider="ollama-cloud",
            model="gemma4:31b",
            api_key=None,
            base_url=None,
            strategy="refusal_inversion",
            dry_run=True,
            interactive=False,
            honcho_key=None,
            honcho_workspace=None,
        )
        captured = capsys.readouterr()
        assert "Dry run complete" in captured.out

    def test_dry_run_openai(self, capsys):
        activate_khaos(
            provider="openai",
            model="gpt-4o",
            api_key="sk-test-fake",
            base_url=None,
            strategy="og_godmode",
            dry_run=True,
            interactive=False,
            honcho_key=None,
            honcho_workspace=None,
        )
        captured = capsys.readouterr()
        assert "Dry run complete" in captured.out

    def test_dry_run_honcho_demo(self, capsys):
        activate_khaos(
            provider="ollama-cloud",
            model="gemma4:31b",
            api_key=None,
            base_url=None,
            strategy="refusal_inversion",
            dry_run=True,
            interactive=False,
            honcho_key="",
            honcho_workspace="khaos",
        )
        captured = capsys.readouterr()
        assert "Dry run complete" in captured.out