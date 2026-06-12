from videogen_mcp.webapp_static import repo_root, webapp_dist_dir


def test_repo_root_is_directory():
    root = repo_root()
    assert root.is_dir()


def test_webapp_dist_missing_without_build(monkeypatch, tmp_path):
    monkeypatch.delenv("VIDEOGEN_WEBAPP_DIR", raising=False)
    monkeypatch.setattr(
        "videogen_mcp.webapp_static.repo_root",
        lambda: tmp_path,
    )
    assert webapp_dist_dir() is None
