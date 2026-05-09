from datetime import datetime
from django.utils import timezone

from .state_store import load_state, save_state

VALID_GESTURES = {"UP", "RIGHT", "LEFT", "DOWN"}

ACTION_COMMANDS = {
    "led_on": {
        "command": {"led": "ON"},
        "message": "Bat den",
    },
    "led_off": {
        "command": {"led": "OFF"},
        "message": "Tat den",
    },
    "motor_on": {
        "command": {"motor": "ON"},
        "message": "Bat quat",
    },
    "motor_off": {
        "command": {"motor": "OFF"},
        "message": "Tat quat",
    },
}


def normalize_sequence(value):
    if isinstance(value, str):
        parts = value.replace(",", " ").split()
    elif isinstance(value, list):
        parts = value
    else:
        raise ValueError("sequence phai la list hoac chuoi")

    sequence = [str(x).strip().upper() for x in parts if str(x).strip()]

    if len(sequence) != 4:
        raise ValueError("sequence phai co dung 4 phan tu")

    for item in sequence:
        if item not in VALID_GESTURES:
            raise ValueError(f"gesture khong hop le: {item}")

    return sequence


def handle_gesture_payload(payload, esp32_ip=None, esp32_port=None):
    state = load_state()

    if esp32_ip:
        state["esp32"]["ip"] = esp32_ip

    if esp32_port:
        state["esp32"]["port"] = int(esp32_port)

    state["esp32"]["last_seen"] = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
    state["last_payload"] = payload

    try:
        if isinstance(payload, dict):
            raw_sequence = payload.get("sequence")
        else:
            raw_sequence = payload

        sequence = normalize_sequence(raw_sequence)
    except Exception as e:
        state["last_message"] = f"Gesture loi: {e}"
        save_state(state)

        return {
            "ok": False,
            "reason": "INVALID_SEQUENCE",
            "message": str(e),
        }

    state["last_gesture"] = sequence

    rules = state.get("gesture_rules", {})

    for action_name, rule_sequence in rules.items():
        if action_name not in ACTION_COMMANDS:
            continue

        try:
            normalized_rule = normalize_sequence(rule_sequence)
        except Exception:
            continue

        if sequence == normalized_rule:
            action = ACTION_COMMANDS[action_name]
            command = action["command"]

            state.update(command)
            state["last_command"] = command
            state["last_message"] = f"Matched {action_name}: {action['message']}"

            save_state(state)
            return command

    state["last_command"] = None
    state["last_message"] = "Khong khop rule nao"
    save_state(state)

    return {
        "ok": False,
        "reason": "NO_MATCHING_RULE",
        "received": sequence,
    }