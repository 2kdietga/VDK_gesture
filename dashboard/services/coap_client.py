import json
import socket

from .coap_protocol import build_post_packet, parse_coap_packet


def post_json(host, port, path, payload, timeout=2):
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    packet, message_id = build_post_packet(path, payload_bytes)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        sock.sendto(packet, (host, int(port)))
        response_data, address = sock.recvfrom(2048)

        response = parse_coap_packet(response_data)
        response_text = response.payload.decode("utf-8", errors="ignore")

        try:
            response_json = json.loads(response_text)
        except Exception:
            response_json = None

        return {
            "ok": True,
            "address": f"{address[0]}:{address[1]}",
            "message_id": message_id,
            "raw": response_text,
            "json": response_json,
        }

    except socket.timeout:
        return {
            "ok": False,
            "reason": "TIMEOUT",
            "message": "Khong nhan duoc response tu ESP32",
        }

    except Exception as e:
        return {
            "ok": False,
            "reason": "ERROR",
            "message": str(e),
        }

    finally:
        sock.close()