# ui/core/constants.py

# Красивые названия для действий одной руки
SINGLE_ACTION_KEYS = [
    "Open Photos",
    "Open Notes",
    "Open Calendar",
    "Take Screenshot",
    "None"
]

# Внутренние ключи для маппинга (используются в коде)
SINGLE_ACTION_MAPPING = {
    "Open Photos": "open_photos",
    "Open Notes": "open_notes",
    "Open Calendar": "open_calendar",
    "Take Screenshot": "take_screenshot",
    "None": "none"
}

# Обратный маппинг (из внутренних ключей в красивые названия)
SINGLE_ACTION_REVERSE = {
    "open_photos": "Open Photos",
    "open_notes": "Open Notes",
    "open_calendar": "Open Calendar",
    "take_screenshot": "Take Screenshot",
    "none": "None"
}

# Красивые названия для действий двух рук
TWO_ACTION_KEYS = [
    "Turn On Music",
    "None"
]

# Внутренние ключи для маппинга двух рук
TWO_ACTION_MAPPING = {
    "Turn On Music": "turn_music",
    "None": "none"
}

# Обратный маппинг для двух рук
TWO_ACTION_REVERSE = {
    "turn_music": "Turn On Music",
    "none": "None"
}

# Дефолтные значения (используем внутренние ключи)
DEFAULT_SINGLE_MAPPING = {
    "is_like": "open_photos",
    "is_dislike": "open_notes",
    "is_stop": "open_calendar",
    "is_okay": "take_screenshot",
}

DEFAULT_TWO_MAPPING = {
    "is_stop is_stop": "turn_music",
    "is_two_stops": "turn_music",
}

# Старые константы для обратной совместимости (если используются где-то еще)
ACTION_DEFINITIONS = {
    "open_photos": "Open Photos",
    "open_notes": "Open Notes",
    "open_calendar": "Open Calendar",
    "take_screenshot": "Take Screenshot",
    "turn_music": "Turn On Music",
}