import pytest
from unittest.mock import patch, MagicMock
from src.actions.two_hands_actions import TwoHandsActions
import pickle

# 1. Проверка инициализации класса
def test_init_default_values():
    obj = TwoHandsActions()
    assert obj.both_hands_detected is False
    assert obj.previous_gesture is None
    assert obj.gesture_count == 0

# 2. get_action с gesture=None
def test_get_action_none():
    obj = TwoHandsActions()
    assert obj.get_action(None) is None

# 3. get_action с gesture=""
def test_get_action_empty_string():
    obj = TwoHandsActions()
    assert obj.get_action("") is None

# 4. get_action с gesture="is_two_stops" (успех)
def test_get_action_is_two_stops_success():
    obj = TwoHandsActions()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        result = obj.get_action("is_two_stops")
        assert result == "🎵 Music opened"

# 5. get_action с gesture="is_two_stops" (ошибка subprocess)
def test_get_action_is_two_stops_subprocess_error():
    obj = TwoHandsActions()
    with patch("subprocess.run", side_effect=Exception("fail")):
        result = obj.get_action("is_two_stops")
        assert result == "❌ Error"

# 6. get_action с gesture="is_two_stops" (ошибка CalledProcessError)
def test_get_action_is_two_stops_called_process_error():
    obj = TwoHandsActions()
    with patch("subprocess.run", side_effect=Exception("fail")):
        result = obj.get_action("is_two_stops")
        assert "Error" in result

# 7. get_action с gesture="unknown_gesture"
def test_get_action_unknown_gesture():
    obj = TwoHandsActions()
    assert obj.get_action("unknown_gesture") is None

# 8. _two_gesture_action вызывает subprocess.run с правильными аргументами
def test_two_gesture_action_subprocess_args():
    obj = TwoHandsActions()
    with patch("subprocess.run") as mock_run:
        obj._two_gesture_action()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "osascript"
        assert args[1] == "-e"

# 9. _two_gesture_action возвращает "🎵 Music opened" при успехе
def test_two_gesture_action_success():
    obj = TwoHandsActions()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        result = obj._two_gesture_action()
        assert result == "🎵 Music opened"

# 10. _two_gesture_action возвращает "❌ Error opening Music" при ошибке subprocess
def test_two_gesture_action_subprocess_error():
    obj = TwoHandsActions()
    with patch("subprocess.run", side_effect=Exception("fail")):
        result = obj._two_gesture_action()
        assert result == "❌ Error"

# 11. _two_gesture_action возвращает "❌ Error" при неожиданной ошибке
def test_two_gesture_action_unexpected_error():
    obj = TwoHandsActions()
    with patch("subprocess.run", side_effect=Exception("fail")):
        result = obj._two_gesture_action()
        assert "Error" in result

# 12. previous_gesture не изменяется после get_action
def test_previous_gesture_not_changed():
    obj = TwoHandsActions()
    obj.previous_gesture = "test"
    obj.get_action("is_two_stops")
    assert obj.previous_gesture == "test"

# 13. gesture_count не изменяется после get_action
def test_gesture_count_not_changed():
    obj = TwoHandsActions()
    obj.gesture_count = 5
    obj.get_action("is_two_stops")
    assert obj.gesture_count == 5

# 14. both_hands_detected не изменяется после get_action
def test_both_hands_detected_not_changed():
    obj = TwoHandsActions()
    obj.both_hands_detected = True
    obj.get_action("is_two_stops")
    assert obj.both_hands_detected is True

# 15. print вызывается с правильным сообщением при распознавании жеста
def test_print_gesture_recognized(capsys):
    obj = TwoHandsActions()
    obj.get_action("is_two_stops")
    captured = capsys.readouterr()
    assert "Gesture recognized: is_two_stops" in captured.out

# 16. print вызывается с правильным сообщением при успешном открытии приложения
def test_print_music_app_opened(capsys):
    obj = TwoHandsActions()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        obj.get_action("is_two_stops")
        captured = capsys.readouterr()
        assert "Music app opened successfully" in captured.out

# 17. print вызывается с правильным сообщением при ошибке subprocess
def test_print_error_opening_music(capsys):
    obj = TwoHandsActions()
    with patch("subprocess.run", side_effect=Exception("fail")):
        obj.get_action("is_two_stops")
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.out

# 18. print вызывается с правильным сообщением при неожиданной ошибке
def test_print_unexpected_error(capsys):
    obj = TwoHandsActions()
    with patch("subprocess.run", side_effect=Exception("fail")):
        obj.get_action("is_two_stops")
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.out

# 19. get_action возвращает None для нераспознанных жестов
def test_get_action_none_for_unrecognized():
    obj = TwoHandsActions()
    assert obj.get_action("not_a_gesture") is None

# 20. get_action возвращает None для пустого жеста
def test_get_action_none_for_empty():
    obj = TwoHandsActions()
    assert obj.get_action("") is None

# 21. get_action возвращает None для None
def test_get_action_none_for_none():
    obj = TwoHandsActions()
    assert obj.get_action(None) is None

# 22. _two_gesture_action не изменяет состояние объекта
def test_two_gesture_action_state_unchanged():
    obj = TwoHandsActions()
    before = (obj.both_hands_detected, obj.previous_gesture, obj.gesture_count)
    with patch("subprocess.run"):
        obj._two_gesture_action()
    after = (obj.both_hands_detected, obj.previous_gesture, obj.gesture_count)
    assert before == after

# 23. _two_gesture_action корректно обрабатывает исключения
def test_two_gesture_action_handles_exceptions():
    obj = TwoHandsActions()
    with patch("subprocess.run", side_effect=Exception("fail")):
        result = obj._two_gesture_action()
        assert "Error" in result

# 24. _two_gesture_action корректно работает при повторных вызовах
def test_two_gesture_action_multiple_calls():
    obj = TwoHandsActions()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        for _ in range(3):
            assert obj._two_gesture_action() == "🎵 Music opened"

# 25. get_action корректно работает при повторных вызовах
def test_get_action_multiple_calls():
    obj = TwoHandsActions()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        for _ in range(3):
            assert obj.get_action("is_two_stops") == "🎵 Music opened"

# 26. сериализация и десериализация класса
def test_pickle_serialization():
    obj = TwoHandsActions()
    obj.both_hands_detected = True
    obj.previous_gesture = "test"
    obj.gesture_count = 42
    data = pickle.dumps(obj)
    obj2 = pickle.loads(data)
    assert obj2.both_hands_detected is True
    assert obj2.previous_gesture == "test"
    assert obj2.gesture_count == 42

