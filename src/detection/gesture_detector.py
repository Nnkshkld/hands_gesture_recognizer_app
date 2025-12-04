import cv2
import mediapipe as mp
import time


class GestureDetector:
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """
        Инициализация детектора жестов с MediaPipe

        Args:
            min_detection_confidence: Минимальная уверенность для детекции руки
            min_tracking_confidence: Минимальная уверенность для отслеживания руки
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Для предотвращения множественных срабатываний
        self.last_gesture = None
        self.last_gesture_time = 0
        self.cooldown = 2.0  # 2 секунды между одинаковыми жестами

        # Индексы ключевых точек руки
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.PINKY_TIP = 20

        self.THUMB_IP = 3
        self.INDEX_PIP = 6
        self.MIDDLE_PIP = 10
        self.RING_PIP = 14
        self.PINKY_PIP = 18

        self.WRIST = 0

    def detect(self, frame):
        """
        Анализирует кадр и возвращает распознанный жест

        Args:
            frame: numpy array изображение BGR из OpenCV

        Returns:
            str: название жеста или None
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return None

        # Проверка cooldown
        current_time = time.time()

        # Если обнаружена одна рука
        if len(results.multi_hand_landmarks) == 1:
            landmarks = results.multi_hand_landmarks[0].landmark
            handedness = results.multi_handedness[0].classification[0].label

            gesture = self._detect_single_hand_gesture(landmarks, handedness)

            if gesture and self._check_cooldown(gesture, current_time):
                self.last_gesture = gesture
                self.last_gesture_time = current_time
                return gesture

        # Если обнаружены две руки
        elif len(results.multi_hand_landmarks) == 2:
            landmarks1 = results.multi_hand_landmarks[0].landmark
            landmarks2 = results.multi_hand_landmarks[1].landmark

            # Проверяем жест "два стопа"
            if self._is_stop_gesture(landmarks1) and self._is_stop_gesture(landmarks2):
                gesture = "is_two_stops"
                if self._check_cooldown(gesture, current_time):
                    self.last_gesture = gesture
                    self.last_gesture_time = current_time
                    return gesture

        return None

    def _check_cooldown(self, gesture, current_time):
        """Проверяет, прошло ли достаточно времени с последнего жеста"""
        if gesture != self.last_gesture:
            return True
        return (current_time - self.last_gesture_time) > self.cooldown

    def _detect_single_hand_gesture(self, landmarks, handedness):
        """Распознает жест одной руки"""

        # Лайк (большой палец вверх)
        if self._is_like_gesture(landmarks):
            return "is_like"

        # Дизлайк (большой палец вниз)
        if self._is_dislike_gesture(landmarks):
            return "is_dislike"

        # Стоп (открытая ладонь)
        if self._is_stop_gesture(landmarks):
            return "is_stop"

        # Окей (большой + указательный формируют круг)
        if self._is_okay_gesture(landmarks):
            return "is_okay"

        return None

    def _is_like_gesture(self, landmarks):
        """Проверяет жест 'лайк' - большой палец вверх, остальные сжаты"""
        thumb_tip = landmarks[self.THUMB_TIP]
        thumb_ip = landmarks[self.THUMB_IP]
        index_tip = landmarks[self.INDEX_TIP]
        index_pip = landmarks[self.INDEX_PIP]
        wrist = landmarks[self.WRIST]

        # Большой палец выше остальных и направлен вверх
        thumb_up = thumb_tip.y < thumb_ip.y < wrist.y

        # Остальные пальцы согнуты
        fingers_folded = (
                index_tip.y > index_pip.y and
                landmarks[self.MIDDLE_TIP].y > landmarks[self.MIDDLE_PIP].y and
                landmarks[self.RING_TIP].y > landmarks[self.RING_PIP].y and
                landmarks[self.PINKY_TIP].y > landmarks[self.PINKY_PIP].y
        )

        return thumb_up and fingers_folded

    def _is_dislike_gesture(self, landmarks):
        """Проверяет жест 'дизлайк' - большой палец вниз, остальные сжаты"""
        thumb_tip = landmarks[self.THUMB_TIP]
        thumb_ip = landmarks[self.THUMB_IP]
        index_tip = landmarks[self.INDEX_TIP]
        index_pip = landmarks[self.INDEX_PIP]
        wrist = landmarks[self.WRIST]

        # Большой палец ниже запястья и направлен вниз
        thumb_down = thumb_tip.y > thumb_ip.y > wrist.y

        # Остальные пальцы согнуты
        fingers_folded = (
                index_tip.y > index_pip.y and
                landmarks[self.MIDDLE_TIP].y > landmarks[self.MIDDLE_PIP].y and
                landmarks[self.RING_TIP].y > landmarks[self.RING_PIP].y and
                landmarks[self.PINKY_TIP].y > landmarks[self.PINKY_PIP].y
        )

        return thumb_down and fingers_folded

    def _is_stop_gesture(self, landmarks):
        """Проверяет жест 'стоп' - открытая ладонь, все пальцы выпрямлены"""
        # Все кончики пальцев выше средних суставов
        fingers_extended = (
                landmarks[self.THUMB_TIP].x > landmarks[self.THUMB_IP].x and
                landmarks[self.INDEX_TIP].y < landmarks[self.INDEX_PIP].y and
                landmarks[self.MIDDLE_TIP].y < landmarks[self.MIDDLE_PIP].y and
                landmarks[self.RING_TIP].y < landmarks[self.RING_PIP].y and
                landmarks[self.PINKY_TIP].y < landmarks[self.PINKY_PIP].y
        )

        return fingers_extended

    def _is_okay_gesture(self, landmarks):
        """Проверяет жест 'окей' - большой и указательный формируют круг"""
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]

        # Расстояние между большим и указательным
        distance = ((thumb_tip.x - index_tip.x) ** 2 +
                    (thumb_tip.y - index_tip.y) ** 2) ** 0.5

        # Остальные пальцы выпрямлены
        other_fingers_up = (
                landmarks[self.MIDDLE_TIP].y < landmarks[self.MIDDLE_PIP].y and
                landmarks[self.RING_TIP].y < landmarks[self.RING_PIP].y and
                landmarks[self.PINKY_TIP].y < landmarks[self.PINKY_PIP].y
        )

        # Если пальцы близко (формируют круг) и остальные подняты
        return distance < 0.05 and other_fingers_up

    def draw_landmarks(self, frame, results=None):
        """
        Рисует ориентиры руки на кадре

        Args:
            frame: изображение для рисования
            results: результаты из self.hands.process() (опционально)

        Returns:
            frame: изображение с нарисованными ориентирами
        """
        if results is None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
                )

        return frame

    def __del__(self):
        """Очистка ресурсов"""
        if hasattr(self, 'hands'):
            self.hands.close()


# Пример использования (для тестирования)
if __name__ == "__main__":
    detector = GestureDetector()
    cap = cv2.VideoCapture(0)

    print("Тестирование распознавания жестов...")
    print("Нажмите 'q' для выхода")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Распознавание жеста
        gesture = detector.detect(frame)

        # Рисуем ориентиры
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.hands.process(frame_rgb)
        frame = detector.draw_landmarks(frame, results)

        # Показываем распознанный жест
        if gesture:
            cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Gesture detection Test', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()