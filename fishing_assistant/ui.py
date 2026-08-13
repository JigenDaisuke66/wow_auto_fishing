"""PyQt5 user interface."""

import os
import time

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig, load_config, save_config
from .texts import text
from .worker import FishingWorker


STYLE = """
QMainWindow, QWidget { background: #f4f7fb; color: #24324a; font-size: 14px; }
QTabWidget::pane { border: 1px solid #dce4ef; border-radius: 10px; background: white; top: -1px; }
QTabBar::tab { background: #e8eef7; padding: 10px 18px; margin-right: 3px; border-radius: 7px 7px 0 0; }
QTabBar::tab:selected { background: #ffffff; color: #1769aa; font-weight: 600; }
QLineEdit, QSpinBox, QDoubleSpinBox, QListWidget, QTextEdit {
    background: white; border: 1px solid #cfd9e7; border-radius: 7px; padding: 7px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #2684ff; }
QPushButton { background: #edf2f8; border: none; border-radius: 7px; padding: 9px 16px; font-weight: 600; }
QPushButton:hover { background: #dfe9f5; }
QPushButton#primary { background: #1677d2; color: white; }
QPushButton#primary:hover { background: #0f68bc; }
QPushButton#danger { background: #fff0f0; color: #b42318; }
QPushButton:disabled { background: #e8ebef; color: #9aa5b1; }
QLabel#title { font-size: 24px; font-weight: 700; color: #183153; }
QLabel#subtitle { color: #66758a; }
QLabel#section { font-size: 16px; font-weight: 700; margin-top: 5px; }
QFrame#status { background: #eaf5ff; border-radius: 8px; }
"""


class FishingAssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.worker: FishingWorker | None = None
        self._closing = False
        self.setWindowTitle(text("window_title"))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setStyleSheet(STYLE)
        self.resize(720, 760)
        self.setMinimumSize(650, 650)
        self._build_ui()
        self._populate_config()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel(text("window_title"))
        title.setObjectName("title")
        subtitle = QLabel(text("subtitle"))
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._general_tab(), text("tab_general"))
        self.tabs.addTab(self._window_tab(), text("tab_window"))
        self.tabs.addTab(self._detection_tab(), text("tab_detection"))
        self.tabs.addTab(self._log_tab(), text("tab_log"))
        layout.addWidget(self.tabs, 1)

        controls = QHBoxLayout()
        controls.addStretch()
        self.stop_button = QPushButton(text("stop"))
        self.stop_button.setObjectName("danger")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_fishing)
        self.start_button = QPushButton(text("start"))
        self.start_button.setObjectName("primary")
        self.start_button.clicked.connect(self.start_fishing)
        controls.addWidget(self.stop_button)
        controls.addWidget(self.start_button)
        layout.addLayout(controls)
        self.setCentralWidget(root)

    def _section(self, value: str) -> QLabel:
        label = QLabel(value)
        label.setObjectName("section")
        return label

    def _general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.addWidget(self._section(text("images")))
        hint = QLabel(text("image_hint"))
        hint.setObjectName("subtitle")
        layout.addWidget(hint)
        self.image_list = QListWidget()
        layout.addWidget(self.image_list, 1)
        buttons = QHBoxLayout()
        add_button = QPushButton(text("add_images"))
        add_button.clicked.connect(self.add_images)
        clear_button = QPushButton(text("clear_images"))
        clear_button.clicked.connect(self.clear_images)
        buttons.addWidget(add_button)
        buttons.addWidget(clear_button)
        buttons.addStretch()
        layout.addLayout(buttons)

        form = QFormLayout()
        self.fishing_hotkey = QLineEdit()
        self.fishing_hotkey.setPlaceholderText("F")
        self.bait_hotkey = QLineEdit()
        self.bait_hotkey.setPlaceholderText("1")
        self.duration = QSpinBox()
        self.duration.setRange(1, 24)
        form.addRow(text("fishing_hotkey"), self.fishing_hotkey)
        form.addRow(text("bait_hotkey"), self.bait_hotkey)
        form.addRow(text("duration"), self.duration)
        layout.addLayout(form)
        return tab

    def _window_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.addWidget(self._section(text("window_title_label")))
        hint = QLabel(text("window_title_hint"))
        hint.setObjectName("subtitle")
        layout.addWidget(hint)
        self.game_window_title = QLineEdit()
        layout.addWidget(self.game_window_title)

        layout.addWidget(self._section(text("afk_settings")))
        form = QFormLayout()
        self.afk_key = QLineEdit()
        range_widget = QWidget()
        range_layout = QHBoxLayout(range_widget)
        range_layout.setContentsMargins(0, 0, 0, 0)
        self.afk_min = QSpinBox()
        self.afk_min.setRange(1, 60)
        self.afk_max = QSpinBox()
        self.afk_max.setRange(1, 60)
        range_layout.addWidget(self.afk_min)
        range_layout.addWidget(QLabel(text("to")))
        range_layout.addWidget(self.afk_max)
        range_layout.addStretch()
        form.addRow(text("afk_key"), self.afk_key)
        form.addRow(text("afk_range"), range_widget)
        layout.addLayout(form)
        layout.addStretch()
        return tab

    def _detection_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(18, 18, 18, 18)
        hint = QLabel(text("detection_hint"))
        hint.setWordWrap(True)
        hint.setObjectName("subtitle")
        layout.addWidget(hint)
        form = QFormLayout()
        self.confidence = self._double_spin(0.1, 1.0, 0.05, 2)
        self.mean_difference = self._double_spin(0, 255, 1, 1)
        self.pixel_threshold = QSpinBox()
        self.pixel_threshold.setRange(1, 255)
        self.pixel_ratio = self._double_spin(0.01, 1.0, 0.01, 2)
        self.confirmation_frames = QSpinBox()
        self.confirmation_frames.setRange(1, 10)
        form.addRow(text("confidence"), self.confidence)
        form.addRow(text("mean_difference"), self.mean_difference)
        form.addRow(text("pixel_threshold"), self.pixel_threshold)
        form.addRow(text("pixel_ratio"), self.pixel_ratio)
        form.addRow(text("confirmation_frames"), self.confirmation_frames)
        layout.addLayout(form)
        layout.addStretch()
        return tab

    def _log_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(18, 18, 18, 18)
        self.status = QLabel(text("ready"))
        self.status.setObjectName("subtitle")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.status)
        layout.addWidget(self.log_output, 1)
        return tab

    @staticmethod
    def _double_spin(minimum: float, maximum: float, step: float, decimals: int) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setSingleStep(step)
        spin.setDecimals(decimals)
        return spin

    def _populate_config(self) -> None:
        self.fishing_hotkey.setText(self.config.fishing_hotkey)
        self.bait_hotkey.setText(self.config.bait_hotkey)
        self.duration.setValue(self.config.duration_hours)
        self.game_window_title.setText(self.config.game_window_title)
        self.afk_key.setText(self.config.afk_key)
        self.afk_min.setValue(self.config.afk_time_min)
        self.afk_max.setValue(self.config.afk_time_max)
        self.confidence.setValue(self.config.confidence_threshold)
        self.mean_difference.setValue(self.config.difference_threshold)
        self.pixel_threshold.setValue(self.config.changed_pixel_threshold)
        self.pixel_ratio.setValue(self.config.changed_pixel_ratio)
        self.confirmation_frames.setValue(self.config.confirmation_frames)
        self._refresh_images()

    def _read_config(self) -> AppConfig:
        config = AppConfig(
            image_paths=list(self.config.image_paths),
            fishing_hotkey=self.fishing_hotkey.text().strip(),
            bait_hotkey=self.bait_hotkey.text().strip(),
            duration_hours=self.duration.value(),
            difference_threshold=self.mean_difference.value(),
            confidence_threshold=self.confidence.value(),
            game_window_title=self.game_window_title.text().strip(),
            afk_time_min=self.afk_min.value(),
            afk_time_max=self.afk_max.value(),
            afk_key=self.afk_key.text().strip(),
            changed_pixel_threshold=self.pixel_threshold.value(),
            changed_pixel_ratio=self.pixel_ratio.value(),
            confirmation_frames=self.confirmation_frames.value(),
        )
        config.normalize()
        return config

    def add_images(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, text("add_images"), "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        for path in paths:
            if path not in self.config.image_paths:
                self.config.image_paths.append(path)
        self._refresh_images()
        self._save()

    def clear_images(self) -> None:
        self.config.image_paths.clear()
        self._refresh_images()
        self._save()

    def _refresh_images(self) -> None:
        self.image_list.clear()
        if not self.config.image_paths:
            self.image_list.addItem(text("no_images"))
            return
        self.image_list.addItems([os.path.basename(path) for path in self.config.image_paths])

    def log(self, message: str) -> None:
        self.log_output.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        self.status.setText(message)

    def _save(self) -> None:
        try:
            self.config = self._read_config()
            save_config(self.config)
        except OSError as exc:
            self.log(f"⚠ 保存配置失败：{exc}")

    def start_fishing(self) -> None:
        self._save()
        if not self.config.image_paths:
            self.log("❌ 请先添加至少一张浮漂模板")
            self.tabs.setCurrentIndex(0)
            return
        if not self.config.fishing_hotkey:
            self.log("❌ 请填写钓鱼快捷键")
            self.tabs.setCurrentIndex(0)
            return
        if not self.config.game_window_title:
            self.log("❌ 请填写游戏窗口标题")
            self.tabs.setCurrentIndex(1)
            return

        self.worker = FishingWorker(self.config, self)
        self.worker.log_signal.connect(self.log)
        self.worker.finished.connect(self._worker_finished)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.tabs.setCurrentIndex(3)
        self.log("▶ 钓鱼程序已启动")
        self.worker.start()

    def stop_fishing(self) -> None:
        if self.worker and self.worker.isRunning():
            self.stop_button.setEnabled(False)
            self.worker.stop()

    def _worker_finished(self) -> None:
        worker = self.worker
        self.worker = None
        if worker:
            worker.deleteLater()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log("■ 钓鱼程序已停止")
        if self._closing:
            QTimer.singleShot(0, self.close)

    def closeEvent(self, event) -> None:
        self._save()
        if self.worker and self.worker.isRunning():
            self._closing = True
            self.worker.stop()
            event.ignore()
            return
        event.accept()
