import json
from pathlib import Path

from viddl.config import Config


def test_from_dict_basic():
    cfg = Config.from_dict({
        "quality": "720p",
        "output_dir": "./videos",
        "audio_only": True,
        "skip_existing": False,
    })
    assert cfg.quality == "720p"
    assert cfg.output_dir == Path("./videos")
    assert cfg.audio_only is True
    assert cfg.skip_existing is False


def test_load_json(tmp_path: Path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"quality": "480p"}), encoding="utf-8")
    cfg = Config.load(p)
    assert cfg.quality == "480p"