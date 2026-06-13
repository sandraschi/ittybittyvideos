import os
import shutil
import tempfile

import pytest

os.environ["ITTYBITTY_ADDONS_DIR"] = tempfile.mkdtemp()

from videogen_mcp.services.addons import (
    ADDON_REGISTRY,
    get_addon,
    get_addons_dir,
    get_total_size_mb,
    is_installed,
    list_addons,
)


def test_addon_registry_has_six_packs():
    assert len(ADDON_REGISTRY) == 6


def test_list_addons_returns_all():
    addons = list_addons()
    assert len(addons) == 6
    assert all("id" in a for a in addons)
    assert all("size_mb" in a for a in addons)


def test_get_addon_known():
    addon = get_addon("beat-pack")
    assert addon is not None
    assert addon.name == "Beat Detection"


def test_get_addon_unknown():
    assert get_addon("nonexistent-pack") is None


def test_is_installed_false_by_default():
    assert is_installed("beat-pack") is False


def test_total_size():
    total = get_total_size_mb()
    assert total > 10000


def test_addons_dir_created():
    d = get_addons_dir()
    assert d.exists()


@pytest.mark.asyncio
async def test_install_addon_placeholder():
    from videogen_mcp.services.addons import install_addon

    result = await install_addon("beat-pack")
    assert result["success"] is True
    assert "placeholder" in result or "already_installed" in result or "installed" in result.get("message", "")


def teardown_module():
    d = os.environ.get("ITTYBITTY_ADDONS_DIR", "")
    if d and os.path.exists(d):
        shutil.rmtree(d, ignore_errors=True)
