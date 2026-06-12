from videogen_mcp.services.config_store import (
    SECRET_MASK,
    read_env_map,
    reload_settings,
    write_env_map,
)


def test_write_env_preserves_secrets(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=sk-real-key\nOPENAI_MODEL=gpt-4o-mini\n", encoding="utf-8")
    monkeypatch.setenv("VIDEOGEN_ENV_FILE", str(env_file))

    write_env_map({"OPENAI_MODEL": "gpt-4.1-mini", "OPENAI_API_KEY": SECRET_MASK})
    data = read_env_map()
    assert data["OPENAI_API_KEY"] == "sk-real-key"
    assert data["OPENAI_MODEL"] == "gpt-4.1-mini"


def test_write_env_updates_new_key(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPSEEK_API_KEY=\n", encoding="utf-8")
    monkeypatch.setenv("VIDEOGEN_ENV_FILE", str(env_file))

    write_env_map({"DEEPSEEK_API_KEY": "sk-new"})
    assert read_env_map()["DEEPSEEK_API_KEY"] == "sk-new"


def test_reload_settings_after_write(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("VIDEOGEN_LLM_PROVIDER=openai\n", encoding="utf-8")
    monkeypatch.setenv("VIDEOGEN_ENV_FILE", str(env_file))
    monkeypatch.delenv("VIDEOGEN_LLM_PROVIDER", raising=False)
    reload_settings()

    write_env_map({"VIDEOGEN_LLM_PROVIDER": "deepseek"})
    settings = reload_settings()
    assert settings.videogen_llm_provider == "deepseek"
