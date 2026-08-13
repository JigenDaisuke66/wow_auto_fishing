"""Template matching and bite-change detection."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

import cv2
import numpy as np
import pyautogui


LogCallback = Callable[[str], None]


@dataclass(frozen=True)
class Template:
    path: str
    gray: np.ndarray

    @property
    def width(self) -> int:
        return self.gray.shape[1]

    @property
    def height(self) -> int:
        return self.gray.shape[0]


@dataclass(frozen=True)
class Match:
    template_path: str
    x: int
    y: int
    width: int
    height: int
    confidence: float


@dataclass(frozen=True)
class ChangeMetrics:
    mean_difference: float
    changed_ratio: float


def load_templates(
    paths: Iterable[str],
    log: Optional[LogCallback] = None,
    unreadable_message: str = "⚠ 无法读取模板：{name}",
) -> list[Template]:
    templates: list[Template] = []
    for path in paths:
        # np.fromfile + imdecode supports Chinese and other Unicode paths on Windows.
        try:
            data = np.fromfile(path, dtype=np.uint8)
            image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
        except (OSError, ValueError):
            image = None
        if image is None or image.size == 0:
            if log:
                log(unreadable_message.format(name=Path(path).name))
            continue
        templates.append(Template(path, image))
    return templates


def screenshot_bgr(region: Optional[tuple[int, int, int, int]] = None) -> np.ndarray:
    screenshot = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)


def find_best_match(
    screenshot: np.ndarray,
    templates: Iterable[Template],
    confidence_threshold: float,
    origin: tuple[int, int] = (0, 0),
) -> Optional[Match]:
    screen_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    best: Optional[Match] = None
    for template in templates:
        if template.height > screen_gray.shape[0] or template.width > screen_gray.shape[1]:
            continue
        result = cv2.matchTemplate(screen_gray, template.gray, cv2.TM_CCOEFF_NORMED)
        _, confidence, _, location = cv2.minMaxLoc(result)
        if confidence >= confidence_threshold and (best is None or confidence > best.confidence):
            best = Match(
                template.path,
                origin[0] + location[0],
                origin[1] + location[1],
                template.width,
                template.height,
                float(confidence),
            )
    return best


def prepare_gray(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (5, 5), 0)


def calculate_change(
    baseline_gray: np.ndarray,
    current_bgr: np.ndarray,
    pixel_threshold: int,
) -> ChangeMetrics:
    current_gray = prepare_gray(current_bgr)
    if baseline_gray.shape != current_gray.shape:
        return ChangeMetrics(0.0, 0.0)
    difference = cv2.absdiff(baseline_gray, current_gray)
    return ChangeMetrics(
        mean_difference=float(np.mean(difference)),
        changed_ratio=float(np.count_nonzero(difference >= pixel_threshold) / difference.size),
    )
