import random

COAP_TYPE_CON = 0
COAP_TYPE_NON = 1
COAP_TYPE_ACK = 2

COAP_CODE_EMPTY = 0
COAP_CODE_GET = 1
COAP_CODE_POST = 2

COAP_CODE_CONTENT = 69        # 2.05
COAP_CODE_BAD_REQUEST = 128   # 4.00
COAP_CODE_NOT_FOUND = 132     # 4.04


class CoapRequest:
    def __init__(self, version, msg_type, token, code, message_id, path, payload):
        self.version = version
        self.msg_type = msg_type
        self.token = token
        self.code = code
        self.message_id = message_id
        self.path = path
        self.payload = payload


def _read_extended(nibble, data, index):
    if nibble < 13:
        return nibble, index

    if nibble == 13:
        return data[index] + 13, index + 1

    if nibble == 14:
        return int.from_bytes(data[index:index + 2], "big") + 269, index + 2

    raise ValueError("option nibble 15 khong hop le")


def parse_coap_packet(data):
    if len(data) < 4:
        raise ValueError("packet qua ngan")

    first = data[0]
    version = first >> 6
    msg_type = (first >> 4) & 0x03
    token_length = first & 0x0F

    if version != 1:
        raise ValueError("chi ho tro CoAP version 1")

    if token_length > 8:
        raise ValueError("token length khong hop le")

    code = data[1]
    message_id = int.from_bytes(data[2:4], "big")

    index = 4
    token = data[index:index + token_length]
    index += token_length

    option_number = 0
    uri_paths = []
    payload = b""

    while index < len(data):
        if data[index] == 0xFF:
            payload = data[index + 1:]
            break

        option_byte = data[index]
        index += 1

        delta_nibble = option_byte >> 4
        length_nibble = option_byte & 0x0F

        delta, index = _read_extended(delta_nibble, data, index)
        length, index = _read_extended(length_nibble, data, index)

        option_number += delta
        value = data[index:index + length]
        index += length

        # Option 11 = Uri-Path
        if option_number == 11:
            uri_paths.append(value.decode("utf-8", errors="ignore"))

    path = "/" + "/".join(uri_paths)

    return CoapRequest(
        version=version,
        msg_type=msg_type,
        token=token,
        code=code,
        message_id=message_id,
        path=path,
        payload=payload,
    )


def build_response(request, payload_bytes, code=COAP_CODE_CONTENT):
    if not isinstance(payload_bytes, bytes):
        raise TypeError("payload_bytes phai la bytes")

    if request.msg_type == COAP_TYPE_CON:
        response_type = COAP_TYPE_ACK
    else:
        response_type = COAP_TYPE_NON

    token_length = len(request.token)

    first = (1 << 6) | (response_type << 4) | token_length

    packet = bytes([
        first,
        code,
        (request.message_id >> 8) & 0xFF,
        request.message_id & 0xFF,
    ])

    packet += request.token

    if payload_bytes:
        packet += b"\xFF" + payload_bytes

    return packet


def _encode_extended(value):
    if value < 13:
        return value, b""

    if value < 269:
        return 13, bytes([value - 13])

    if value < 65805:
        return 14, int(value - 269).to_bytes(2, "big")

    raise ValueError("option qua lon")


def _encode_option(delta, value):
    if isinstance(value, str):
        value = value.encode("utf-8")

    delta_nibble, delta_extra = _encode_extended(delta)
    length_nibble, length_extra = _encode_extended(len(value))

    return bytes([(delta_nibble << 4) | length_nibble]) + delta_extra + length_extra + value


def build_post_packet(path, payload_bytes):
    if path.startswith("/"):
        path = path[1:]

    message_id = random.randint(0, 65535)
    token = random.randbytes(2) if hasattr(random, "randbytes") else bytes([
        random.randint(0, 255),
        random.randint(0, 255),
    ])

    token_length = len(token)

    first = (1 << 6) | (COAP_TYPE_CON << 4) | token_length

    packet = bytes([
        first,
        COAP_CODE_POST,
        (message_id >> 8) & 0xFF,
        message_id & 0xFF,
    ])

    packet += token

    previous_option_number = 0

    for part in path.split("/"):
        if not part:
            continue

        option_number = 11  # Uri-Path
        delta = option_number - previous_option_number
        packet += _encode_option(delta, part)
        previous_option_number = option_number

    if payload_bytes:
        packet += b"\xFF" + payload_bytes

    return packet, message_id