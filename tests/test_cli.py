import json
from pathlib import Path

from label_sections import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_json_inventory_contains_offsets(capsys):
    assert main([str(FIXTURES / "mda_full.html"), "--json"]) == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["components"]
    first = payload["components"][0]
    assert {"marker", "start", "end", "pattern", "snippet"} <= set(first)
    output = Path(payload["output"])
    assert output.exists()
    output.unlink()


def test_in_place_creates_backup(tmp_path):
    source = tmp_path / "article.html"
    source.write_text((FIXTURES / "minimal.html").read_text(encoding="utf-8"), encoding="utf-8")
    assert main([str(source), "--in-place"]) == 0
    assert source.with_suffix(".html.bak").exists()
    assert "<!-- BEGIN: TOPBAR -->" in source.read_text(encoding="utf-8")


def test_audit_only_outputs_coverage_without_writing(tmp_path, capsys):
    source = tmp_path / "article.html"
    source.write_text((FIXTURES / "minimal.html").read_text(encoding="utf-8"), encoding="utf-8")
    assert main([str(tmp_path), "--audit-only"]) == 0
    out = capsys.readouterr().out
    assert "Component Coverage Report" in out
    assert not (tmp_path / "article.labeled.html").exists()
