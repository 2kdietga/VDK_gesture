import json
from pathlib import Path
from copy import deepcopy
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parents[2]
STATE_PATH = BASE_DIR / "storage" / "state.json"

DEFAULT_STATE = {
    "esp32": {
        "ip": "192.168.2.50",
        "port": 5683,
        "last_seen": None,
    },
    "led": "OFF",
    "motor": "OFF",
    "last_gesture": [],
    "last_payload": None,
    "last_command": None,
    "last_message": "Chua co du lieu",
    "gesture_rules": {
        "led_on": ["LEFT", "RIGHT", "LEFT", "RIGHT"],
        "led_off": ["RIGHT", "LEFT", "RIGHT", "LEFT"],
        "motor_on": ["UP", "RIGHT", "UP", "RIGHT"],
        "motor_off": ["DOWN", "LEFT", "DOWN", "LEFT"],
    },
}


def deep_merge(default, current):
    result = deepcopy(default)

    for key, value in current.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_state():
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not STATE_PATH.exists():
        save_state(DEFAULT_STATE)
        return deepcopy(DEFAULT_STATE)

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return deep_merge(DEFAULT_STATE, data)
    except Exception:
        save_state(DEFAULT_STATE)
        return deepcopy(DEFAULT_STATE)


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = STATE_PATH.with_name(f"{STATE_PATH.stem}.{uuid4().hex}.tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    try:
        tmp_path.replace(STATE_PATH)
    except PermissionError:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        try:
            tmp_path.unlink()
        except (FileNotFoundError, PermissionError):
            pass
