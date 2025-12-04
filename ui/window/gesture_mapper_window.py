from typing import Dict
import sys
import os

import cv2
from PyQt6.QtCore import Qt, QProcess, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QMessageBox,
    QStackedWidget,
    QHBoxLayout,
    QSizePolicy,
)

# Импорты констант и функций
from ui.core.constants import (
    DEFAULT_SINGLE_MAPPING,
    DEFAULT_TWO_MAPPING,
    SINGLE_ACTION_KEYS,
    TWO_ACTION_KEYS,
    SINGLE_ACTION_MAPPING,
    TWO_ACTION_MAPPING,
    SINGLE_ACTION_REVERSE,
    TWO_ACTION_REVERSE,
)
from ui.handlers.interface import apply_mapping


class GestureMapperWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture Mapper")
        self.resize(1200, 750)

        # State
        self.single_combos: Dict[str, QComboBox] = {}
        self.two_combos: Dict[str, QComboBox] = {}

        # Camera state
        self.cap = None
        self.camera_timer: QTimer | None = None
        self._camera_running = False
        self.video_label: QLabel | None = None

        # Gesture recognition (будет инициализировано при старте)
        self.gesture_detector = None
        self.single_actions = None
        self.two_actions = None

        # External Process
        self.process = QProcess(self)

        # Root stacked UI
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # Build screens
        self._build_welcome_screen()
        self._build_mapper_screen()

        # Start on welcome
        self.stack.setCurrentIndex(0)
        self._apply_styles()
        self.statusBar().showMessage("Ready")

    def _build_welcome_screen(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Nice to meet you!")
        title.setObjectName("heroTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton("Let's start")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self.on_welcome_start_clicked)

        layout.addStretch(1)
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(30)
        layout.addWidget(self.start_btn, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        self.stack.addWidget(page)

    def _build_mapper_screen(self):
        page = QWidget(self)
        page.setObjectName("mapperPage")
        root_layout = QVBoxLayout(page)
        root_layout.setContentsMargins(40, 35, 40, 35)
        root_layout.setSpacing(20)

        # Main title
        title = QLabel("Customization options")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root_layout.addWidget(title)

        # Content layout - две колонки
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # ===== ЛЕВАЯ ПАНЕЛЬ - Опции жестов =====
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(18)

        # Маппинг жестов с красивыми названиями
        gesture_data = [
            ("is_like", "Like"),
            ("is_stop", "Stop"),
            ("is_okay", "Okay"),
            ("is_dislike", "Dislike"),
            ("is_two_stops", "Two hands"),
        ]

        for gesture_key, gesture_label in gesture_data:
            row = QHBoxLayout()
            row.setSpacing(20)

            # Label для жеста
            label = QLabel(gesture_label)
            label.setObjectName("gestureLabel")
            label.setFixedWidth(120)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # ComboBox для действия
            if gesture_key == "is_two_stops":
                combo = QComboBox()
                combo.setObjectName("actionCombo")
                combo.addItems(TWO_ACTION_KEYS)
                default_two = DEFAULT_TWO_MAPPING.get("is_stop is_stop", "turn_music")
                pretty_name = TWO_ACTION_REVERSE.get(default_two, "None")
                try:
                    combo.setCurrentIndex(TWO_ACTION_KEYS.index(pretty_name))
                except ValueError:
                    pass
                self.two_combos["is_stop is_stop"] = combo
                self.two_combos["is_two_stops"] = combo
            else:
                combo = QComboBox()
                combo.setObjectName("actionCombo")
                combo.addItems(SINGLE_ACTION_KEYS)
                default_action = DEFAULT_SINGLE_MAPPING.get(gesture_key, "none")
                pretty_name = SINGLE_ACTION_REVERSE.get(default_action, "None")
                try:
                    combo.setCurrentIndex(SINGLE_ACTION_KEYS.index(pretty_name))
                except ValueError:
                    pass
                self.single_combos[gesture_key] = combo

            row.addWidget(label)
            row.addWidget(combo, 1)
            left_layout.addLayout(row)

        left_layout.addStretch()
        content_layout.addWidget(left_panel, 1)

        # ===== ПРАВАЯ ПАНЕЛЬ - Камера =====
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.video_label = QLabel("Camera preview")
        self.video_label.setObjectName("videoLabel")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout.addWidget(self.video_label)

        content_layout.addWidget(right_panel, 1)

        root_layout.addLayout(content_layout, 1)

        # ===== НИЖНИЕ КНОПКИ =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 0, 0, 00)

        start_btn = QPushButton("Start")
        start_btn.setObjectName("startButton")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self.on_start_processing_clicked)

        stop_btn = QPushButton("Stop")
        stop_btn.setObjectName("stopButton")
        stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        stop_btn.clicked.connect(self.on_stop_camera_clicked)

        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("resetButton")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self.on_reset_clicked)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(70)
        buttons_layout.setContentsMargins(20, 0, 0, 0)

        # Левая группа
        buttons_layout.addWidget(start_btn)
        buttons_layout.addWidget(stop_btn)

        buttons_layout.addStretch()  # растягиваем пространство между левыми и правыми кнопками

        # Правая группа
        buttons_layout.addWidget(reset_btn)

        root_layout.addLayout(buttons_layout)

        self.stack.addWidget(page)

    # -------- Actions --------
    def on_welcome_start_clicked(self):
        self.stack.setCurrentIndex(1)

    def on_start_processing_clicked(self):
        try:
            # 1. Apply current mappings
            self.on_apply_clicked()

            # 2. Initialize gesture recognition if not already done
            self._initialize_gesture_recognition()

            # 3. Start the camera
            self.start_camera(0)

        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Start Error")
            msg.setText(f"Failed to start:\n{e}")
            msg.exec()

    def on_stop_camera_clicked(self):
        self.stop_camera()
        self.statusBar().showMessage("Camera stopped.", 3000)

    def on_apply_clicked(self):
        # Преобразуем красивые названия в внутренние ключи
        single_map = {
            k: SINGLE_ACTION_MAPPING.get(self.single_combos[k].currentText(), "none")
            for k in self.single_combos
        }
        two_choice_pretty = self.two_combos["is_stop is_stop"].currentText()
        two_choice = TWO_ACTION_MAPPING.get(two_choice_pretty, "none")
        two_map = {k: two_choice for k in self.two_combos}
        apply_mapping(single_map, two_map)
        self.statusBar().showMessage("Gesture mapping applied", 3000)

    def on_reset_clicked(self):
        for k, combo in self.single_combos.items():
            default = DEFAULT_SINGLE_MAPPING.get(k, "none")
            pretty_name = SINGLE_ACTION_REVERSE.get(default, "None")
            try:
                combo.setCurrentIndex(SINGLE_ACTION_KEYS.index(pretty_name))
            except ValueError:
                pass
        two_default = DEFAULT_TWO_MAPPING.get("is_stop is_stop", "turn_music")
        pretty_name_two = TWO_ACTION_REVERSE.get(two_default, "None")
        try:
            self.two_combos["is_stop is_stop"].setCurrentIndex(TWO_ACTION_KEYS.index(pretty_name_two))
        except ValueError:
            pass
        self.statusBar().showMessage("Defaults restored. Click Start to apply and begin.", 3000)

    # -------- Gesture Recognition Initialization --------
    def _initialize_gesture_recognition(self):
        """Инициализация модулей распознавания жестов"""
        try:
            # Добавляем путь к проекту
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # Импортируем необходимые классы
            from src.detection.gesture_detector import GestureDetector
            from src.actions.single_hand_actions import SingleHandActions
            from src.actions.two_hands_actions import TwoHandsActions

            # Инициализируем детектор жестов
            if self.gesture_detector is None:
                self.gesture_detector = GestureDetector()
                print("GestureDetector initialized")

            # Инициализируем обработчики действий
            if self.single_actions is None:
                self.single_actions = SingleHandActions()
                print("SingleHandActions initialized")

            if self.two_actions is None:
                self.two_actions = TwoHandsActions()
                print("TwoHandsActions initialized")

            print("Gesture recognition initialized successfully")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize gesture recognition: {e}")

    # -------- Camera Helpers --------
    def start_camera(self, index: int = 0):
        if self._camera_running:
            self.statusBar().showMessage("Camera is already running.", 2000)
            return

        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            raise RuntimeError(f"Cannot open camera index {index}")

        self._camera_running = True
        if self.camera_timer is None:
            self.camera_timer = QTimer(self)
            self.camera_timer.timeout.connect(self._update_frame)
        self.camera_timer.start(30)  # ~33 FPS
        self.statusBar().showMessage(f"Camera started (index {index})", 3000)

    def stop_camera(self):
        if self.camera_timer:
            self.camera_timer.stop()
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        self.cap = None
        self._camera_running = False
        if self.video_label:
            self.video_label.clear()
            self.video_label.setText("Camera preview")

    def _update_frame(self):
        """Обновление кадра с камеры и распознавание жестов"""
        if not self.cap or not self._camera_running:
            return

        ok, frame = self.cap.read()
        if not ok:
            return

        frame = cv2.flip(frame, 1)  # Mirror effect

        # РАСПОЗНАВАНИЕ ЖЕСТОВ
        if self.gesture_detector:
            gesture = self.gesture_detector.detect(frame)

            if gesture:
                print(f"Detected gesture: {gesture}")

                # Обработка жеста двумя руками
                if gesture == "is_two_stops":
                    if self.two_actions:
                        result = self.two_actions.get_action(gesture)
                        if result:
                            self.statusBar().showMessage(f"Action: {result}", 2000)

                # Обработка жеста одной рукой
                else:
                    if self.single_actions:
                        result = self.single_actions.get_action(gesture)
                        if result:
                            self.statusBar().showMessage(f"Action: {result}", 2000)

                # Визуализация жеста на экране
                cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Рисуем ориентиры руки
            frame_rgb_for_detection = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.gesture_detector.hands.process(frame_rgb_for_detection)
            frame = self.gesture_detector.draw_landmarks(frame, results)

        # Отображение кадра
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    # -------- Style --------
    def _apply_styles(self):
        self.setStyleSheet("""
        QMainWindow {
            background: white;
        }

        /* Welcome Screen */
        QStackedWidget > QWidget:first-child {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #e0e7ff,
                stop:1 #a5b4fc);
        }

        QLabel#heroTitle {
            color: #1f2937;
            font-size: 56px;
            font-weight: 700;
        }

        QPushButton#startButton {
            background-color: #1e1b8f;
            color: white;
            border: none;
            border-radius: 25px;
            padding: 14px 52px;
            font-size: 20px;
            font-weight: 600;
        }

        QPushButton#startButton:hover {
            background-color: #2522a8;
        }

QWidget#mapperPage {
    background: qlineargradient(x1:0, y1:1, x2:1, y2:0,
        stop:0 #f7fcff,   /* светлый – левый нижний */
        stop:1 #c0cbcf);  /* тёмный – правый верхний */
}

        QLabel#mainTitle {
            font-size: 38px;
            font-weight: 700;
            color: #1f2937;
        }

        /* Left Panel - Gesture Options */
        QWidget#leftPanel {
            background: white;
            border-radius: 25px;
        }

        QLabel#gestureLabel {
            color: #1f2937;
            font-size: 20px;
            font-weight: 500;
        }

        QComboBox#actionCombo {
            background: #e5e7eb;
            color: #374151;
            border: none;
            border-radius: 25px;
            padding: 12px 20px;
            font-size: 17px;
            font-weight: 400;
            min-height: 42px;
        }

        QComboBox#actionCombo:hover {
            background: #d1d5db;
        }

        QComboBox#actionCombo::drop-down {
            border: none;
            width: 35px;
        }

        QComboBox#actionCombo QAbstractItemView {
            background: white;
            color: #374151;
            border: 1px solid #e5e7eb;
            border-radius: 15px;
            selection-background-color: #e5e7eb;
            padding: 8px;
            font-size: 17px;
        }

        /* Right Panel - Camera */
        QWidget#rightPanel {
            background: white;
            border-radius: 25px;
        }

        QLabel#videoLabel {
            font-size: 22px;
            font-weight: 500;
            color: #9ca3af;
        }

        /* Bottom Buttons */
        QPushButton#startButton {
            background-color: #15803d;
            color: white;
            border: 2px solid #15803d;
            border-radius: 25px;
            padding: 12px 40px;
            font-size: 20px;
            font-weight: 600;
            min-width: 130px;
        }

        QPushButton#startButton:hover {
            background-color: #16a34a;
        }

        QPushButton#stopButton {
            background-color: #1e1b8f;
            color: white;
            border: 2px solid #1e1b8f;
            border-radius: 25px;
            padding: 12px 40px;
            font-size: 20px;
            font-weight: 600;
            min-width: 130px;
        }

       QPushButton#stopButton:hover {
            background-color: #2522a8;
        }

        QPushButton#resetButton {
            background-color: white;
            color: #374151;
            border: 2px solid #e5e7eb;
            border-radius: 25px;
            padding: 12px 40px;
            font-size: 20px;
            font-weight: 600;
            min-width: 130px;
        }

        QPushButton#resetButton:hover {
            background-color: #f9fafb;
        }

        QStatusBar {
            background: transparent;
            color: #374151;
            font-size: 14px;
        }
        """)

    def closeEvent(self, event):
        """Очистка ресурсов при закрытии окна"""
        self.stop_camera()
        event.accept()