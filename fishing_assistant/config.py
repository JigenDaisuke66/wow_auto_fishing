"""Application configuration and JSON persistence."""

from dataclasses import asdict, dataclass, fields
import json
from pathlib import Path
from typing import Any


CONFIG_FILE = Path("fishing_assistant_config.json")


@dataclass
class AppConfig:
    image_paths: list[str] = None
    fishing_hotkey: str = ""
    bait_hotkey: str = ""
    duration_hours: int = 2
    difference_threshold: float = 12.0
    confidence_threshold: float = 0.7
    game_window_title: str = "魔兽世界"
    afk_time_min: int = 10
    afk_time_max: int = 15
    afk_key: str = "space"
    changed_pixel_threshold: int = 20
    changed_pixel_ratio: float = 0.08
    confirmation_frames: int = 2

    def __post_init__(self) -> None:
        if self.image_paths is None:
            self.image_paths = []

    def normalize(self) -> None:
        self.image_paths = [str(path) for path in self.image_paths]
        self.afk_time_min = max(1, int(self.afk_time_min))
        self.afk_time_max = max(self.afk_time_min, int(self.afk_time_max))
        self.confirmation_frames = max(1, int(self.confirmation_frames))


def load_config(path: Path = CONFIG_FILE) -> AppConfig:
    if not path.exists():
        return AppConfig()
    try:
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        allowed = {field.name for field in fields(AppConfig)}
        config = AppConfig(**{key: value for key, value in raw.items() if key in allowed})
        config.normalize()
        return config
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return AppConfig()


def save_config(config: AppConfig, path: Path = CONFIG_FILE) -> None:
    config.normalize()
    path.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
