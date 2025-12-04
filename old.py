import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

both_hands_detected = False
previous_gesture = None
gesture_count = 0
GESTURE_THRESHOLD = 50
DELAY_SECONDS = 10


def classify_single_hand(hand_landmarks):
    """Определяет жест для одной руки."""
    finger_tips = [4, 8, 12, 16, 20]
    finger_base = [2, 5, 9, 13, 17]

    fingers_extended = []
    for tip, base in zip(finger_tips[1:], finger_base[1:]):
        if (
            hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y - 0.02
            and hand_landmarks.landmark[tip].z < hand_landmarks.landmark[base].z
        ):
            fingers_extended.append(True)
        else:
            fingers_extended.append(False)

    thumb_tip = hand_landmarks.landmark[4]
    thumb_base = hand_landmarks.landmark[2]

    if thumb_tip.y < thumb_base.y - 0.05 and thumb_tip.z < thumb_base.z:
        fingers_extended.insert(0, True)
    else:
        fingers_extended.insert(0, False)

    is_fist = all(
        abs(hand_landmarks.landmark[tip].x - hand_landmarks.landmark[base].x) < 0.05
        for tip, base in zip(finger_tips, finger_base)
    )

    if not is_fist and fingers_extended[0] and not any(fingers_extended[1:]):
        return "👍"

    if not is_fist and not fingers_extended[0] and not any(fingers_extended[1:]):
        return "👎"

    if all(fingers_extended):
        return "✋"

    index_tip = hand_landmarks.landmark[8]
    thumb_tip = hand_landmarks.landmark[4]

    if abs(index_tip.x - thumb_tip.x) < 0.05 and abs(index_tip.y - thumb_tip.y) < 0.05:
        return "👌"

    return None


def classify_hands(hand_landmarks_list):
    """Обрабатывает обе руки и определяет общий жест."""
    global both_hands_detected, previous_gesture, gesture_count

    num_hands = len(hand_landmarks_list)

    # Проверка на две руки
    if num_hands == 2:
        if not both_hands_detected:
            print("🚀 Обнаружены обе руки!")
            both_hands_detected = True
    else:
        both_hands_detected = False  # Сброс флага

    # Классификация каждой руки
    detected_gestures = [classify_single_hand(hand) for hand in hand_landmarks_list]

    # Если обе руки делают одинаковый жест
    if num_hands == 2 and detected_gestures[0] == detected_gestures[1]:
        gesture = f"{detected_gestures[0]} {detected_gestures[1]}"
    else:
        gesture = ", ".join([g for g in detected_gestures if g])

    if gesture:
        if gesture == previous_gesture:
            gesture_count += 1
        else:
            previous_gesture = gesture
            gesture_count = 1  # Сброс счётчика, если жест изменился

        # Если жест был 50 раз подряд, вывести его и сделать паузу
        if gesture_count >= GESTURE_THRESHOLD:
            print(f"🎉 Жест {gesture} стабильно распознан 50 раз! Ожидание {DELAY_SECONDS} секунд...")
            time.sleep(DELAY_SECONDS)
            gesture_count = 0  # Сбросить счетчик после задержки


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        classify_hands(results.multi_hand_landmarks)

        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
