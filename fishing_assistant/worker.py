"""Cooperatively stoppable fishing worker."""

import random
import time
from typing import Optional

import pyautogui
import win32con
import win32gui
from PyQt5.QtCore import QThread, pyqtSignal

from .config import AppConfig
from .vision import calculate_change, find_best_match, load_templates, prepare_gray, screenshot_bgr


class FishingWorker(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config

    def stop(self) -> None:
        self.requestInterruption()
        self.log_signal.emit("🛑 已请求安全停止，正在结束当前操作…")

    def _active(self) -> bool:
        return not self.isInterruptionRequested()

    def _wait(self, seconds: float) -> bool:
        """Interruptible wait; returns False when stop was requested."""
        deadline = time.monotonic() + seconds
        while self._active() and time.monotonic() < deadline:
            time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
        return self._active()

    def _schedule_afk(self) -> float:
        return time.monotonic() + random.uniform(
            self.config.afk_time_min * 60,
            self.config.afk_time_max * 60,
        )

    def _maybe_afk(self, next_afk_at: float) -> float:
        if time.monotonic() < next_afk_at:
            return next_afk_at
        if self.config.afk_key:
            pyautogui.press(self.config.afk_key)
            self.log_signal.emit(f"⏱ 防挂机：按下 {self.config.afk_key}")
        return self._schedule_afk()

    def run(self) -> None:
        templates = load_templates(self.config.image_paths, self.log_signal.emit)
        if not templates:
            self.log_signal.emit("❌ 没有可读取的浮漂模板")
            return

        end_at = time.monotonic() + self.config.duration_hours * 3600
        next_bait_at = time.monotonic() if self.config.bait_hotkey else float("inf")
        next_afk_at = self._schedule_afk()

        while self._active() and time.monotonic() < end_at:
            try:
                region = self._activate_and_get_region()
                if region is None:
                    self.log_signal.emit("❌ 游戏窗口激活失败，请检查窗口标题")
                    if not self._wait(3):
                        break
                    continue

                if time.monotonic() >= next_bait_at:
                    self.log_signal.emit("🪱 使用鱼饵…")
                    pyautogui.press(self.config.bait_hotkey)
                    next_bait_at = time.monotonic() + 660
                    if not self._wait(2):
                        break

                self.log_signal.emit("🎣 抛竿钓鱼…")
                pyautogui.press(self.config.fishing_hotkey)
                if not self._wait(1.5):
                    break

                caught, next_afk_at = self._detect_cast(region, templates, next_afk_at)
                if not caught and self._active():
                    self.log_signal.emit("🟡 本轮未确认咬钩，准备重新抛竿")
                if not self._wait(3):
                    break
            except Exception as exc:
                self.log_signal.emit(f"❌ 运行错误：{exc}")
                if not self._wait(3):
                    break

    def _detect_cast(self, region, templates, next_afk_at: float) -> tuple[bool, float]:
        cast_deadline = time.monotonic() + 20
        match = None
        while self._active() and time.monotonic() < cast_deadline:
            screen = screenshot_bgr(region)
            match = find_best_match(screen, templates, self.config.confidence_threshold, region[:2])
            if match:
                self.log_signal.emit(
                    f"🔍 找到浮漂，置信度 {match.confidence:.2f}"
                )
                break
            next_afk_at = self._maybe_afk(next_afk_at)
            if not self._wait(0.35):
                return False, next_afk_at

        if not match:
            return False, next_afk_at

        target_x = match.x + max(1, match.width - 10)
        target_y = match.y + max(1, match.height - 10)
        pyautogui.moveTo(target_x, target_y, duration=0.25)
        baseline = prepare_gray(screenshot_bgr((match.x, match.y, match.width, match.height)))
        consecutive = 0

        while self._active() and time.monotonic() < cast_deadline:
            current = screenshot_bgr((match.x, match.y, match.width, match.height))
            metrics = calculate_change(baseline, current, self.config.changed_pixel_threshold)
            changed = (
                metrics.mean_difference >= self.config.difference_threshold
                and metrics.changed_ratio >= self.config.changed_pixel_ratio
            )
            consecutive = consecutive + 1 if changed else 0
            self.log_signal.emit(
                f"📊 差异 {metrics.mean_difference:.1f} / 像素比例 {metrics.changed_ratio:.1%} "
                f"/ 确认 {consecutive}/{self.config.confirmation_frames}"
            )
            if consecutive >= self.config.confirmation_frames:
                self.log_signal.emit("🟢 已确认咬钩，右键收杆")
                pyautogui.click(button="right")
                return True, next_afk_at
            next_afk_at = self._maybe_afk(next_afk_at)
            if not self._wait(0.1):
                break
        return False, next_afk_at

    def _activate_and_get_region(self) -> Optional[tuple[int, int, int, int]]:
        hwnd = win32gui.FindWindow(None, self.config.game_window_title)
        if not hwnd:
            return None
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        screen_left, screen_top = win32gui.ClientToScreen(hwnd, (left, top))
        screen_right, screen_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
        width, height = screen_right - screen_left, screen_bottom - screen_top
        if width <= 0 or height <= 0:
            return None
        self._wait(0.2)
        return screen_left, screen_top, width, height
