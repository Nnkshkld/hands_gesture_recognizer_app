import cv2
import mediapipe as mp

from src.handlers import HandsProcessor
from src.settings.config import Settings

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def process_video():
    cap = cv2.VideoCapture(Settings().camera_index)
    hands = mp_hands.Hands()
    processor = HandsProcessor()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            processor.classify_hands(results.multi_hand_landmarks)
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
