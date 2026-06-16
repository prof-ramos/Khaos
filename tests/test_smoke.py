"""Smoke tests for KHAOS GodMode Activation Kernel.

All tests run via dry_run=True -- no real provider is contacted.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

import pytest

import activate
from activate import DEFAULT_PROVIDERS, TEMPLATES, activate_khaos


class TestCLIProviderDefaults:
    def test_known_providers(self):
        assert "ollama-cloud" in DEFAULT_PROVIDERS
        assert "openai" in DEFAULT_PROVIDERS
        assert "anthropic" in DEFAULT_PROVIDERS
        assert "ollama-local" in DEFAULT_PROVIDERS
        assert "openrouter" in DEFAULT_PROVIDERS
        assert "xai" in DEFAULT_PROVIDERS

    def test_ollama_cloud_defaults(self):
        provider = DEFAULT_PROVIDERS["ollama-cloud"]
        assert provider["default_model"] == "gemma4:31b"
        assert provider["base_url"] == "https://ollama.com/v1"
        assert provider["api_key_env"] == "OLLAMA_API_KEY"

    def test_openai_defaults(self):
        provider = DEFAULT_PROVIDERS["openai"]
        assert provider["default_model"] == "gpt-4o"
        assert provider["base_url"] == "https://api.openai.com/v1"

    def test_ollama_local_no_key_env(self):
        provider = DEFAULT_PROVIDERS["ollama-local"]
        assert provider["api_key_env"] is None


class TestStrategyTemplates:
    def test_all_strategies_present(self):
        required = {"refusal_inversion", "og_godmode", "direct_godmode", "pliny_love"}
        assert required.issubset(set(TEMPLATES.keys()))

    def test_strategies_non_empty(self):
        for name, prompt in TEMPLATES.items():
            assert len(prompt) > 50, f"Strategy '{name}' is too short ({len(prompt)} chars)"


class TestDryRun:
    @pytest.fixture(autouse=True)
    def _clean_env(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_API_KEY", "test-dummy-key")
        monkeypatch.delenv("HONCHO_API_KEY", raising=False)
        monkeypatch.delenv("KHAOS_HONCHO_KEY", raising=False)
        monkeypatch.delenv("HONCHO_WORKSPACE_ID", raising=False)
        monkeypatch.delenv("KHAOS_HONCHO_WORKSPACE", raising=False)
        return

    def test_dry_run_ollama_cloud(self):
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


class TestEnvLoading:
    def test_khos_env_loading_is_explicit(self, tmp_path, monkeypatch):
        env_key = "KHAOS_TEST_IMPORT_SIDE_EFFECT"
        monkeypatch.delenv(env_key, raising=False)

        env_file = tmp_path / ".khos.env"
        env_file.write_text(f'{env_key}="loaded-on-demand"\n')

        assert os.getenv(env_key) is None
        activate.load_khos_env(env_file)
        assert os.getenv(env_key) == "loaded-on-demand"

    def test_khos_env_does_not_override_existing_env(self, tmp_path, monkeypatch):
        env_key = "KHAOS_TEST_ENV_PRECEDENCE"
        monkeypatch.setenv(env_key, "from-shell")

        env_file = tmp_path / ".khos.env"
        env_file.write_text(f"{env_key}=from-file\n")

        activate.load_khos_env(env_file)
        assert os.getenv(env_key) == "from-shell"


class TestCLIEntrypoint:
    def test_main_dry_run(self, monkeypatch, capsys):
        monkeypatch.setenv("OLLAMA_API_KEY", "test-dummy-key")
        monkeypatch.delenv("HONCHO_API_KEY", raising=False)
        monkeypatch.delenv("KHAOS_HONCHO_KEY", raising=False)
        monkeypatch.delenv("HONCHO_WORKSPACE_ID", raising=False)
        monkeypatch.delenv("KHAOS_HONCHO_WORKSPACE", raising=False)

        with patch.object(activate, "init_honcho") as init_honcho_mock:
            result = activate.main(["--dry-run"])
            init_honcho_mock.assert_not_called()

        captured = capsys.readouterr()
        assert result is None
        assert "Dry run complete" in captured.out
