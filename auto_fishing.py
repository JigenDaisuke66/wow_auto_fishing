"""Windows entry point for the fishing assistant."""

import sys

from PyQt5.QtWidgets import QApplication

from fishing_assistant.ui import FishingAssistantWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Fishing Assistant")
    font = app.font()
    font.setFamily("Microsoft YaHei UI")
    app.setFont(font)

    window = FishingAssistantWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
