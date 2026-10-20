"""Release metadata and translation consistency."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components/ksem_ws"


def test_manifest_and_hacs():
    manifest = json.loads((COMPONENT / "manifest.json").read_text())
    assert manifest["version"] == "0.1.0"
    assert manifest["config_flow"] is True
    assert manifest["iot_class"] == "local_push"
    assert manifest["requirements"] == []
    assert json.loads((ROOT / "hacs.json").read_text())["homeassistant"] == "2025.6.0"
    assert len(list((ROOT / "custom_components").iterdir())) == 1


def test_translations():
    en = json.loads((COMPONENT / "translations/en.json").read_text())
    de = json.loads((COMPONENT / "translations/de.json").read_text())
    assert en == json.loads((COMPONENT / "strings.json").read_text())
    assert set(en["entity"]["sensor"]) == set(de["entity"]["sensor"])
    assert len(en["entity"]["sensor"]) == 6
    assert set(en["config"]["error"]) == set(de["config"]["error"])
