import subprocess
import os
import time


class SingleHandActions:
    def get_action(self, gesture):
        """Главный метод для обработки жестов одной рукой"""
        print(f"Gesture recognized: {gesture}")

        if gesture == "is_like":
            return self._like_gesture_action()
        elif gesture == "is_dislike":
            return self._dislike_gesture_action()
        elif gesture == "is_stop":
            return self._stop_gesture_action()
        elif gesture == "is_okay":
            return self._okay_gesture_action()
        else:
            return None

    def _like_gesture_action(self):
        """Если жест 'лайк', то открывается галерея (Фото)"""
        print("Opening Photos...")
        subprocess.Popen(["open", "-a", "Photos"])
        return "👍"

    def _dislike_gesture_action(self):
        """Если жест 'дизлайк', то открываются Заметки"""
        print("Opening Notes...")
        subprocess.Popen(["open", "-a", "Notes"])
        return "👎"

    def _stop_gesture_action(self):
        """Если жест 'стоп', то открывается Календарь"""
        print("Opening Calendar...")
        subprocess.Popen(["open", "-a", "Calendar"])
        return "✋"

    def _okay_gesture_action(self):
        """Если жест 'окей', то делается скриншот"""
        print("Taking screenshot...")
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = os.path.expanduser(f"~/Desktop/screenshot_{timestamp}.png")
        subprocess.Popen(["screencapture", screenshot_path])
        return "👌"