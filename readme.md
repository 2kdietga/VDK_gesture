# ESP32 Gesture Dashboard

Du an nay la mot ung dung Django dung de giao tiep voi ESP32 qua CoAP. ESP32 gui gesture len may tinh, server xu ly gesture de:

- dieu khien LED va motor theo chuoi 4 gesture da cau hinh;
- hien thi trang thai ESP32, payload gan nhat va lenh gan nhat tren dashboard;
- choi game 2D don gian bang gesture don `UP`, `DOWN`, `LEFT`, `RIGHT`.

## Thanh phan chinh

- `manage.py`: lenh quan ly Django.
- `coap_server.py`: server CoAP rieng, lang nghe UDP port `5683`, nhan request tu ESP32 tai route `/gesture`.
- `dashboard/views.py`: cac view cua web dashboard, trang game, API state va form gui lenh.
- `dashboard/services/coap_protocol.py`: ham parse/build goi CoAP co ban.
- `dashboard/services/coap_client.py`: client CoAP de Django gui lenh nguoc ve ESP32 tai route `/command`.
- `dashboard/services/gesture_logic.py`: logic phan loai payload gesture va quyet dinh hanh dong.
- `dashboard/services/state_store.py`: luu trang thai hien tai vao `storage/state.json`.
- `templates/dashboard/home.html`: giao dien dashboard dieu khien va cau hinh rule.
- `templates/dashboard/entertainment.html`: game me cung 2D dieu khien bang phim mui ten hoac gesture ESP32.

## Cach chay

Chay ca Django dashboard va CoAP server bang mot lenh:

```powershell
python manage.py runall
```

Mac dinh lenh nay se mo:

```text
Django dashboard: http://0.0.0.0:8000
CoAP server:      udp://0.0.0.0:5683
```

Truy cap tren may tinh:

```text
http://127.0.0.1:8000/
```

Trang game:

```text
http://127.0.0.1:8000/entertainment/
```

Neu chi muon chay rieng Django:

```powershell
python manage.py runserver 0.0.0.0:8000
```

Neu chi muon chay rieng CoAP:

```powershell
python .\coap_server.py
```

## Luong hoat dong

1. ESP32 gui CoAP `POST /gesture` toi IP may tinh, port `5683`.
2. `coap_server.py` nhan packet UDP, parse CoAP va doc payload.
3. Payload duoc dua vao `handle_gesture_payload()` trong `gesture_logic.py`.
4. Neu payload chi co 1 gesture, vi du `UP`, server xem day la lenh cho game:
   - cap nhat `last_move`;
   - tang `gesture_event_id`;
   - khong so rule LED/motor.
5. Neu payload co dung 4 gesture, server xem day la chuoi dieu khien:
   - so voi cac rule trong `state["gesture_rules"]`;
   - neu khop thi cap nhat `led` hoac `motor`;
   - neu khong khop thi tra ve `NO_MATCHING_RULE`.
6. Trang dashboard va trang game doc `/api/state/` de cap nhat giao dien.
7. Khi bam nut bat/tat tren dashboard, Django gui CoAP `POST /command` nguoc ve ESP32.

## Dinh dang payload tu ESP32

Gesture don de choi game:

```text
UP
```

Hoac JSON:

```json
{"gesture": "UP"}
```

Chuoi 4 gesture de dieu khien LED/motor:

```json
{"sequence": ["LEFT", "RIGHT", "LEFT", "RIGHT"]}
```

Cac gesture hop le:

```text
UP, DOWN, LEFT, RIGHT
```

## Rule mac dinh

Rule mac dinh nam trong `dashboard/services/state_store.py`:

```text
led_on:    LEFT RIGHT LEFT RIGHT
led_off:   RIGHT LEFT RIGHT LEFT
motor_on:  UP RIGHT UP RIGHT
motor_off: DOWN LEFT DOWN LEFT
```

Co the thay doi rule tren dashboard bang cach bam vao tung o gesture va nhan phim mui ten.

## Ghi chu khi test

- May tinh va ESP32 can o cung mang LAN.
- ESP32 phai gui CoAP den IP cua may tinh, khong phai `127.0.0.1`.
- Windows Firewall co the chan UDP port `5683`; neu ESP32 khong gui len duoc, can cho phep Python qua firewall.
- Khi debug, xem terminal chay `runall`; server se in `Payload raw` va `Response`.
