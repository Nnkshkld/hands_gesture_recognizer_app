import os
import sys
from typing import Dict

from PyQt6.QtWidgets import QMessageBox


def apply_mapping(single_map: Dict[str, str], two_map: Dict[str, str]) -> None:
    """
    Monkey-patch action routing so gestures call the selected named action.
    - single_map: Maps gesture name (e.g., 'is_like') to action key (e.g., 'open_photos').
    - two_map: Maps gesture name (e.g., 'is_two_stops') to action key (e.g., 'turn_music').
    """
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from src.actions.single_hand_actions import SingleHandActions
        from src.actions.two_hands_actions import TwoHandsActions

        # Store original methods if not already stored
        if not hasattr(SingleHandActions, "_orig_get_action"):
            SingleHandActions._orig_get_action = SingleHandActions.get_action
        if not hasattr(TwoHandsActions, "_orig_get_action"):
            TwoHandsActions._orig_get_action = TwoHandsActions.get_action

        # Store the UI mapping on the classes
        SingleHandActions._ui_mapping = dict(single_map)
        TwoHandsActions._ui_mapping = dict(two_map)

        def _patched_single_get_action(self, gesture: str):
            mapping = getattr(self, "_ui_mapping", {})
            action_key = mapping.get(gesture)

            action_map = {
                "open_photos": self._like_gesture_action,
                "open_notes": self._dislike_gesture_action,
                "open_calendar": self._stop_gesture_action,
                "take_screenshot": self._okay_gesture_action,
                "none": lambda: None,
            }

            action_func = action_map.get(action_key)
            return action_func() if action_func else self._orig_get_action(gesture)

        def _patched_two_get_action(self, gesture: str):
            mapping = getattr(self, "_ui_mapping", {})
            action_key = mapping.get(gesture)

            action_map = {
                "turn_music": self._two_gesture_action,
                "none": lambda: None,
            }

            action_func = action_map.get(action_key)
            return action_func() if action_func else self._orig_get_action(gesture)

        # Apply the patches
        SingleHandActions.get_action = _patched_single_get_action
        TwoHandsActions.get_action = _patched_two_get_action

    except Exception as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Apply Mapping Error")
        msg.setText(f"Failed to apply gesture mapping:\n{e}")
        msg.exec()
