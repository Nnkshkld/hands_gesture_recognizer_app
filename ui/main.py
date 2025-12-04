import sys

from PyQt6.QtWidgets import QApplication

from ui.handlers import GestureMapperWindow

"""
Главный файл для запуска Gesture Mapper приложения
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.window.gesture_mapper_window import GestureMapperWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gesture Mapper")

    window = GestureMapperWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()