import subprocess


class TwoHandsActions:
    def __init__(self):
        self.both_hands_detected = False
        self.previous_gesture = None
        self.gesture_count = 0

    def get_action(self, gesture):
        print(f"Gesture recognized: {gesture}")
        if gesture == "is_two_stops":
            return self._two_gesture_action()
        else:
            return None

    def _two_gesture_action(self):
        """Если жест 'две открытых ладони', то открывает приложение Музыка"""
        try:
            # AppleScript для открытия приложения Музыка
            script = '''
            tell application "Music"
                activate
            end tell
            '''

            subprocess.run(["osascript", "-e", script], check=True)
            print("Music app opened successfully")
            return "🎵 Music opened"

        except subprocess.CalledProcessError as e:
            print(f"Error opening Music app: {e}")
            return "❌ Error opening Music"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "❌ Error"