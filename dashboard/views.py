from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .services.coap_client import post_json
from .services.gesture_logic import ACTION_COMMANDS, normalize_sequence
from .services.state_store import load_state, save_state


def dashboard_home(request):
    state = load_state()

    rules_text = {}
    for key, value in state.get("gesture_rules", {}).items():
        rules_text[key] = " ".join(value)

    context = {
        "state": state,
        "rules_text": rules_text,
    }

    return render(request, "dashboard/home.html", context)


def entertainment(request):
    return render(request, "dashboard/entertainment.html")


@require_POST
def save_config(request):
    state = load_state()

    esp32_ip = request.POST.get("esp32_ip", "").strip()
    esp32_port = request.POST.get("esp32_port", "").strip()

    if esp32_ip:
        state["esp32"]["ip"] = esp32_ip

    if esp32_port:
        try:
            state["esp32"]["port"] = int(esp32_port)
        except ValueError:
            state["last_message"] = "Port ESP32 khong hop le"
            save_state(state)
            return redirect("dashboard_home")

    new_rules = {}

    try:
        for action_name in ACTION_COMMANDS.keys():
            raw_rule = request.POST.get(action_name, "")
            new_rules[action_name] = normalize_sequence(raw_rule)

        state["gesture_rules"] = new_rules
        state["last_message"] = "Da luu cau hinh thanh cong"

    except Exception as e:
        state["last_message"] = f"Luu cau hinh that bai: {e}"

    save_state(state)
    return redirect("dashboard_home")


@require_POST
def send_command(request):
    action_name = request.POST.get("action")

    if action_name not in ACTION_COMMANDS:
        state = load_state()
        state["last_message"] = "Lenh khong hop le"
        save_state(state)
        return redirect("dashboard_home")

    state = load_state()

    command = ACTION_COMMANDS[action_name]["command"]
    esp32_ip = state["esp32"]["ip"]
    esp32_port = state["esp32"]["port"]

    result = post_json(
        host=esp32_ip,
        port=esp32_port,
        path="/command",
        payload=command,
    )

    if result["ok"]:
        state.update(command)
        state["last_command"] = command
        state["last_message"] = f"Da gui {command} toi ESP32. Response: {result.get('raw')}"
    else:
        state["last_message"] = f"Gui lenh that bai: {result}"

    save_state(state)
    return redirect("dashboard_home")


def state_api(request):
    return JsonResponse(load_state(), json_dumps_params={"ensure_ascii": False})
