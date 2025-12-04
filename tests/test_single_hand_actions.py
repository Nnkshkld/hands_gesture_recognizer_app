import pytest
from src.actions.single_hand_actions import SingleHandActions
import subprocess
import time
import os

@pytest.fixture
def actions():
    return SingleHandActions()

def test_like_gesture_action(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    result = actions.get_action("is_like")
    assert result == "👍"
    assert called['cmd'] == ["open", "-a", "Photos"]

def test_dislike_gesture_action(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    result = actions.get_action("is_dislike")
    assert result == "👎"
    assert called['cmd'] == ["open", "-a", "Notes"]

def test_stop_gesture_action(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    result = actions.get_action("is_stop")
    assert result == "✋"
    assert called['cmd'] == ["open", "-a", "Calendar"]

def test_okay_gesture_action(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    monkeypatch.setattr(time, "strftime", lambda fmt: "2024-01-01_12-00-00")
    monkeypatch.setattr(os.path, "expanduser", lambda path: "/mocked/path/screenshot_2024-01-01_12-00-00.png")
    result = actions.get_action("is_okay")
    assert result == "👌"
    assert called['cmd'][0] == "screencapture"
    assert called['cmd'][1].endswith("screenshot_2024-01-01_12-00-00.png")

def test_unknown_gesture(actions):
    result = actions.get_action("unknown_gesture")
    assert result is None

def test_like_gesture_action_multiple(monkeypatch, actions):
    called = []
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.append(cmd))
    for _ in range(3):
        result = actions.get_action("is_like")
        assert result == "👍"
    assert called == [["open", "-a", "Photos"]] * 3

def test_dislike_gesture_action_multiple(monkeypatch, actions):
    called = []
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.append(cmd))
    for _ in range(2):
        result = actions.get_action("is_dislike")
        assert result == "👎"
    assert called == [["open", "-a", "Notes"]] * 2

def test_stop_gesture_action_multiple(monkeypatch, actions):
    called = []
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.append(cmd))
    for _ in range(4):
        result = actions.get_action("is_stop")
        assert result == "✋"
    assert called == [["open", "-a", "Calendar"]] * 4

def test_okay_gesture_action_multiple(monkeypatch, actions):
    called = []
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.append(cmd))
    monkeypatch.setattr(time, "strftime", lambda fmt: "2024-01-01_12-00-00")
    monkeypatch.setattr(os.path, "expanduser", lambda path: "/mocked/path/screenshot_2024-01-01_12-00-00.png")
    for _ in range(2):
        result = actions.get_action("is_okay")
        assert result == "👌"
    assert all(cmd[0] == "screencapture" for cmd in called)

def test_like_gesture_action_case(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    result = actions.get_action("IS_LIKE".lower())
    assert result == "👍"
    assert called['cmd'] == ["open", "-a", "Photos"]

def test_dislike_gesture_action_case(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    result = actions.get_action("IS_DISLIKE".lower())
    assert result == "👎"
    assert called['cmd'] == ["open", "-a", "Notes"]

def test_stop_gesture_action_case(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    result = actions.get_action("IS_STOP".lower())
    assert result == "✋"
    assert called['cmd'] == ["open", "-a", "Calendar"]

def test_okay_gesture_action_case(monkeypatch, actions):
    called = {}
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: called.setdefault('cmd', cmd))
    monkeypatch.setattr(time, "strftime", lambda fmt: "2024-01-01_12-00-00")
    monkeypatch.setattr(os.path, "expanduser", lambda path: "/mocked/path/screenshot_2024-01-01_12-00-00.png")
    result = actions.get_action("IS_OKAY".lower())
    assert result == "👌"
    assert called['cmd'][0] == "screencapture"

def test_private_like(monkeypatch, actions):
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: None)
    assert actions._like_gesture_action() == "👍"

def test_private_dislike(monkeypatch, actions):
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: None)
    assert actions._dislike_gesture_action() == "👎"

def test_private_stop(monkeypatch, actions):
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: None)
    assert actions._stop_gesture_action() == "✋"

def test_private_okay(monkeypatch, actions):
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: None)
    monkeypatch.setattr(time, "strftime", lambda fmt: "2024-01-01_12-00-00")
    monkeypatch.setattr(os.path, "expanduser", lambda path: "/mocked/path/screenshot_2024-01-01_12-00-00.png")
    assert actions._okay_gesture_action() == "👌"

def test_no_side_effects(monkeypatch, actions):
    monkeypatch.setattr(subprocess, "Popen", lambda cmd: None)
    before = actions.__dict__.copy()
    actions.get_action("is_like")
    after = actions.__dict__.copy()
    assert before == after

def test_invalid_type(actions):
    assert actions.get_action(12345) is None

def test_none_gesture(actions):
    assert actions.get_action(None) is None

def test_empty_string_gesture(actions):
    assert actions.get_action("") is None

def test_whitespace_gesture(actions):
    assert actions.get_action("   ") is None

def test_partial_gesture(actions):
    assert actions.get_action("is_li") is None

def test_similar_gesture(actions):
    assert actions.get_action("is_likes") is None
