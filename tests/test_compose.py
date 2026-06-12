from videogen_mcp.providers.base import SubtitleEntry
from videogen_mcp.services.compose import _build_srt, _format_time


def test_format_time_zero():
    assert _format_time(0) == "00:00:00,000"


def test_format_time_complex():
    assert _format_time(3661.5) == "01:01:01,500"


def test_format_time_fractional():
    assert _format_time(1.234) == "00:00:01,234"


def test_build_srt_empty():
    assert _build_srt([]) is None


def test_build_srt_creates_file():
    subs = [
        SubtitleEntry(start=0.0, end=2.0, text="Hello world."),
        SubtitleEntry(start=2.5, end=5.0, text="Second line."),
    ]
    path = _build_srt(subs)
    assert path is not None
    assert path.exists()
    content = path.read_text()
    assert "Hello world." in content
    assert "00:00:00,000 --> 00:00:02,000" in content
    path.unlink()


def test_build_srt_sequential_indices():
    subs = [SubtitleEntry(start=float(i), end=float(i + 1), text=f"Line {i}") for i in range(3)]
    path = _build_srt(subs)
    content = path.read_text()
    assert "1\n" in content
    assert "2\n" in content
    assert "3\n" in content
    path.unlink()
