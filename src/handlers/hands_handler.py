import time
from typing import List, Optional

from src.settings.constants import FINGER_TIPS, FINGER_BASES, GESTURE_THRESHOLD
from src.models import GestureSet
from src.actions import SingleHandActions, TwoHandsActions


class HandsProcessor:
    def __init__(self):
        self.gesture = GestureSet
        self.previous_gesture: Optional[str] = None
        self.gesture_count: int = 0

    def classify_hands(self, hand_landmarks_list: List) -> None:
        num_hands = len(hand_landmarks_list)
        detected_gestures = [self.classify_single_hand(hand) for hand in hand_landmarks_list if hand]

        gesture = self._get_combined_gesture(detected_gestures, num_hands)
        if gesture:
            self._process_detected_gesture(gesture, num_hands)

    def classify_single_hand(self, hand_landmarks) -> Optional[str]:
        """
        Classifies a single hand gesture based on the extended fingers.
        :param hand_landmarks: A list of landmarks for a single hand.
        :return: A string representing the detected gesture.
        """

        fingers_extended = [
            self._is_finger_extended(hand_landmarks, tip, base) for tip, base in zip(FINGER_TIPS[1:], FINGER_BASES[1:])
        ]
        fingers_extended.insert(0, self._is_thumb_extended(hand_landmarks))

        return self._identify_gesture(hand_landmarks, fingers_extended)

    def _is_finger_extended(self, hand_landmarks, tip: int, base: int) -> bool:
        """
        Checks if the finger (except the thumb) is extended.
        :param hand_landmarks: Coordinates of the joints of the hand.
        :param tip: Index of the fingertip.
        :param base: Index of the base of the finger.
        :return: True if the finger is extended, otherwise False.
        """

        return (
            hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y - 0.02
            and hand_landmarks.landmark[tip].z < hand_landmarks.landmark[base].z
        )

    def _is_thumb_extended(self, hand_landmarks) -> bool:
        """
        Checks if the thumb is extended.
        :param hand_landmarks: Coordinates of the hand joints.
        :return: True if the thumb is bent, otherwise False.
        """

        thumb_tip = hand_landmarks.landmark[4]
        thumb_base = hand_landmarks.landmark[2]
        return thumb_tip.y < thumb_base.y - 0.05 and thumb_tip.z < thumb_base.z

    def _identify_gesture(self, hand_landmarks, fingers_extended: List[bool]) -> Optional[str]:
        """
        Determines the gesture type based on finger position.
        :param hand_landmarks: Coordinates of the joints of the hand.
        :param fingers_extended: A list of flags indicating which fingers are extended.
        :return: Name of the gesture or None if the gesture is not recognized.
        """

        is_fist = all(
            abs(hand_landmarks.landmark[tip].x - hand_landmarks.landmark[base].x) < 0.05
            for tip, base in zip(FINGER_TIPS, FINGER_BASES)
        )

        if not is_fist and fingers_extended[0] and not any(fingers_extended[1:]):
            return self.gesture.LIKE.value
        if not is_fist and not fingers_extended[0] and not any(fingers_extended[1:]):
            return self.gesture.DISLIKE.value
        if all(fingers_extended):
            return self.gesture.STOP.value

        index_tip = hand_landmarks.landmark[8]
        thumb_tip = hand_landmarks.landmark[4]
        if abs(index_tip.x - thumb_tip.x) < 0.05 and abs(index_tip.y - thumb_tip.y) < 0.05:
            return self.gesture.OKAY.value

        return None

    def _get_combined_gesture(self, detected_gestures: List[str], num_hands: int) -> Optional[str]:
        """
        Forms a string with gestures of both hands if they match.
        :param detected_gestures: List of gestures of each hand.
        :param num_hands: Number of detected hands.
        :return: String with joined gestures or None if there are no gestures.
        """

        if num_hands == 2 and detected_gestures[0] == detected_gestures[1]:
            return f"{detected_gestures[0]} {detected_gestures[1]}"
        return ", ".join(g for g in detected_gestures if g)

    def _process_detected_gesture(self, gesture: str, num_hands: int) -> None:
        """
        Processes the recognized gesture: checks for repetitions and calls the appropriate action.
        :param gesture: Recognized gesture.
        :param num_hands: Number of hands detected.
        """

        if gesture == self.previous_gesture:
            self.gesture_count += 1
        else:
            self.previous_gesture = gesture
            self.gesture_count = 1

        if self.gesture_count >= GESTURE_THRESHOLD:
            action_class = TwoHandsActions if num_hands == 2 else SingleHandActions
            action_class().get_action(gesture)
            time.sleep(2)
