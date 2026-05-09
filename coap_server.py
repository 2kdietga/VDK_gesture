import json
import os
import socket
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VDK.settings")
django.setup()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dashboard.services.coap_protocol import (
    COAP_CODE_BAD_REQUEST,
    COAP_CODE_CONTENT,
    COAP_CODE_NOT_FOUND,
    COAP_CODE_POST,
    build_response,
    parse_coap_packet,
)
from dashboard.services.gesture_logic import handle_gesture_payload


HOST = "0.0.0.0"
PORT = 5683


def json_bytes(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


def main():
    host = HOST
    port = PORT

    if len(sys.argv) >= 2:
        host = sys.argv[1]

    if len(sys.argv) >= 3:
        port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print(f"CoAP server dang lang nghe udp://{host}:{port}")
    print("Route: POST /gesture")
    print()

    while True:
        data, address = sock.recvfrom(2048)
        client_ip, client_port = address

        try:
            request = parse_coap_packet(data)

            print("===== NHAN COAP REQUEST =====")
            print("From:", client_ip, client_port)
            print("Path:", request.path)
            print("Code:", request.code)
            payload_raw = request.payload.decode("utf-8", errors="replace")
            print("Payload raw:", payload_raw)

            if request.code != COAP_CODE_POST:
                response_data = {
                    "ok": False,
                    "reason": "METHOD_NOT_ALLOWED",
                    "message": "Chi ho tro POST",
                }
                response = build_response(
                    request,
                    json_bytes(response_data),
                    code=COAP_CODE_BAD_REQUEST,
                )
                sock.sendto(response, address)
                continue

            if request.path != "/gesture":
                response_data = {
                    "ok": False,
                    "reason": "NOT_FOUND",
                    "message": "Route khong ton tai",
                }
                response = build_response(
                    request,
                    json_bytes(response_data),
                    code=COAP_CODE_NOT_FOUND,
                )
                sock.sendto(response, address)
                continue

            try:
                payload_text = payload_raw
                payload = json.loads(payload_text)
            except Exception:
                payload = payload_raw

            result = handle_gesture_payload(
                payload=payload,
                esp32_ip=client_ip,
                esp32_port=client_port,
            )

            response = build_response(
                request,
                json_bytes(result),
                code=COAP_CODE_CONTENT,
            )

            sock.sendto(response, address)

            print("Response:", result)
            print("=============================")
            print()

        except Exception as e:
            print("Loi xu ly CoAP:", e)
            print()


if __name__ == "__main__":
    main()
