import json
import threading
import time
from typing import Any

from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt

OPTIONS_PATH = "/data/options.json"

app = Flask(__name__)


def load_options() -> dict[str, Any]:
    defaults = {
        "mqtt_host": "core-mosquitto",
        "mqtt_port": 1883,
        "mqtt_username": "",
        "mqtt_password": "",
        "mqtt_base_topic": "cs2_bridge",
        "discovery_prefix": "homeassistant",
        "publish_discovery": True,
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            defaults.update(data)
    except FileNotFoundError:
        print("No /data/options.json found, using defaults", flush=True)
    except Exception as e:
        print(f"Failed reading options: {e}", flush=True)
    return defaults


OPTIONS = load_options()
BASE = str(OPTIONS["mqtt_base_topic"]).rstrip("/")
DISCOVERY = str(OPTIONS["discovery_prefix"]).rstrip("/")
DEVICE_ID = "cs2_gsi_bridge"
DEVICE_NAME = "CS2 GSI Bridge"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
if OPTIONS.get("mqtt_username"):
    client.username_pw_set(
        OPTIONS.get("mqtt_username"),
        OPTIONS.get("mqtt_password", ""),
    )

_connected = False
_state_lock = threading.Lock()
_latest_state: dict[str, Any] = {}
_discovered_entities: set[str] = set()
_last_light_cache: dict[str, str] = {
    "mode": "",
    "color": "",
    "pulse": "",
    "blink_interval_ms": "",
    "recommended_color": "",
}
_bomb_planted_monotonic: float | None = None


def on_connect(c, userdata, flags, reason_code, properties=None):
    global _connected
    _connected = reason_code == 0
    print(f"MQTT connected: {reason_code}", flush=True)
    if _connected and OPTIONS.get("publish_discovery", True):
        publish_static_discovery()


def on_disconnect(c, userdata, flags, reason_code, properties=None):
    global _connected
    _connected = False
    print(f"MQTT disconnected: {reason_code}", flush=True)


client.on_connect = on_connect
client.on_disconnect = on_disconnect


def mqtt_loop():
    while True:
        try:
            client.connect(OPTIONS["mqtt_host"], int(OPTIONS["mqtt_port"]), 60)
            client.loop_forever(retry_first_connection=True)
        except Exception as e:
            print(f"MQTT loop error: {e}", flush=True)
            time.sleep(5)


def publish(topic: str, payload: Any, retain: bool = False):
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    client.publish(topic, text, qos=1, retain=retain)


def deep_get(data: dict, *keys, default=None):
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def sanitize_topic_part(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum() or ch in ["_", "-"]:
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


def flatten_to_topics(prefix: str, value: Any) -> dict[str, str]:
    result: dict[str, str] = {}

    def _walk(path: str, val: Any):
        if isinstance(val, dict):
            for k, v in val.items():
                key = sanitize_topic_part(str(k))
                _walk(f"{path}/{key}" if path else key, v)
        elif isinstance(val, list):
            for idx, v in enumerate(val):
                _walk(f"{path}/{idx}", v)
        else:
            topic = f"{prefix}/{path}" if path else prefix
            if val is None:
                result[topic] = ""
            elif isinstance(val, bool):
                result[topic] = "true" if val else "false"
            else:
                result[topic] = str(val)

    _walk("", value)
    return result


def icon_for_path(path: str) -> str:
    p = path.lower()
    mapping = [
        ("bomb/countdown", "mdi:timer-outline"),
        ("bomb/state", "mdi:bomb"),
        ("round/phase", "mdi:flag-outline"),
        ("round/bomb", "mdi:bomb"),
        ("phase_countdowns/phase_ends_in", "mdi:timer-sand"),
        ("player/state/health", "mdi:heart"),
        ("player/state/armor", "mdi:shield"),
        ("player/state/flashed", "mdi:flash"),
        ("player/state/smoked", "mdi:smoke"),
        ("player/state/burning", "mdi:fire"),
        ("player/state/money", "mdi:cash"),
        ("player/team", "mdi:account-group"),
        ("map/name", "mdi:map"),
        ("map/mode", "mdi:map-legend"),
    ]
    for key, icon in mapping:
        if p.endswith(key):
            return icon
    return "mdi:information-outline"


def friendly_name_for_path(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    return "CS2 GSI Bridge " + " ".join(part.replace("_", " ").title() for part in parts)


def publish_sensor_discovery(object_id: str, name: str, state_topic: str, icon: str, unit: str | None = None):
    payload = {
        "name": name,
        "unique_id": f"{DEVICE_ID}_{object_id}",
        "state_topic": state_topic,
        "icon": icon,
        "device": {
            "identifiers": [DEVICE_ID],
            "name": DEVICE_NAME,
            "manufacturer": "OpenAI",
            "model": "CS2 GSI MQTT Bridge (Python Full State)",
        },
    }
    if unit:
        payload["unit_of_measurement"] = unit
    publish(f"{DISCOVERY}/sensor/{DEVICE_ID}/{object_id}/config", payload, retain=True)


def publish_binary_sensor_discovery(object_id: str, name: str, state_topic: str, payload_on: str, payload_off: str, icon: str):
    payload = {
        "name": name,
        "unique_id": f"{DEVICE_ID}_{object_id}",
        "state_topic": state_topic,
        "payload_on": payload_on,
        "payload_off": payload_off,
        "icon": icon,
        "device": {
            "identifiers": [DEVICE_ID],
            "name": DEVICE_NAME,
            "manufacturer": "OpenAI",
            "model": "CS2 GSI MQTT Bridge (Python Full State)",
        },
    }
    publish(f"{DISCOVERY}/binary_sensor/{DEVICE_ID}/{object_id}/config", payload, retain=True)


def publish_static_discovery():
    publish_sensor_discovery("light_mode", "CS2 GSI Bridge Light Mode", f"{BASE}/light/mode", "mdi:lightbulb-group")
    publish_sensor_discovery("light_color", "CS2 GSI Bridge Light Color", f"{BASE}/light/color", "mdi:palette")
    publish_sensor_discovery("recommended_color", "CS2 GSI Bridge Recommended Color", f"{BASE}/light/recommended_color", "mdi:palette")
    publish_sensor_discovery("blink_interval_ms", "CS2 GSI Bridge Blink Interval", f"{BASE}/light/blink_interval_ms", "mdi:lightbulb-auto", "ms")
    publish_binary_sensor_discovery("light_pulse", "CS2 GSI Bridge Light Pulse", f"{BASE}/light/pulse", "ON", "OFF", "mdi:lightbulb-on-outline")
    publish(f"{BASE}/light/pulse", "OFF", retain=True)


def maybe_publish_dynamic_discovery(flat_path: str, topic: str):
    object_id = f"state_{sanitize_topic_part(flat_path.replace('/', '_'))}"
    if object_id in _discovered_entities:
        return

    unit = None
    fp = flat_path.lower()
    if fp.endswith("health"):
        unit = "hp"
    elif fp.endswith("armor"):
        unit = "armor"
    elif fp.endswith("phase_ends_in") or fp.endswith("countdown"):
        unit = "s"
    elif fp.endswith("flashed") or fp.endswith("smoked") or fp.endswith("burning"):
        unit = "%"
    elif fp.endswith("blink_interval_ms"):
        unit = "ms"

    publish_sensor_discovery(
        object_id=object_id,
        name=friendly_name_for_path(flat_path),
        state_topic=topic,
        icon=icon_for_path(flat_path),
        unit=unit,
    )
    _discovered_entities.add(object_id)


def calc_visual_period_seconds(time_left: float) -> float:
    if time_left <= 0:
        return 0.15
    return max(0.15, 0.1 + 0.9 * (time_left / 40.0))


def derive_light_state(data: dict[str, Any]) -> dict[str, Any]:
    round_phase = str(deep_get(data, "round", "phase", default="") or "")
    round_bomb = str(deep_get(data, "round", "bomb", default="") or "")
    bomb_state = str(deep_get(data, "bomb", "state", default=round_bomb) or "")
    bomb_countdown = to_float(deep_get(data, "bomb", "countdown", default=0))
    flashed = to_float(deep_get(data, "player", "state", "flashed", default=0))
    burning = to_float(deep_get(data, "player", "state", "burning", default=0))
    smoked = to_float(deep_get(data, "player", "state", "smoked", default=0))
    health = to_float(deep_get(data, "player", "state", "health", default=0))
    team = str(deep_get(data, "player", "team", default="") or "")

    light_mode = "steady"
    light_color = "off"
    blink_interval_ms = 0

    planted = (bomb_state.lower() == "planted" or round_bomb.lower() == "planted")

    if planted:
        if bomb_countdown > 0 and bomb_countdown <= 1.15:
            light_mode = "finale"
            light_color = "red"
            blink_interval_ms = 0
        else:
            light_mode = "blink"
            light_color = "red"
            blink_interval_ms = int(calc_visual_period_seconds(bomb_countdown if bomb_countdown > 0 else 40.0) * 1000)
    elif bomb_state.lower() == "defused" or round_bomb.lower() == "defused":
        light_mode = "flash"
        light_color = "blue"
    elif bomb_state.lower() == "exploded" or round_bomb.lower() == "exploded":
        light_mode = "steady"
        light_color = "red"
    elif flashed > 0:
        light_mode = "flash"
        light_color = "flash_white"
    elif burning > 0:
        light_mode = "steady"
        light_color = "orange_red"
    elif smoked > 0:
        light_mode = "steady"
        light_color = "dim_white"
    elif health > 0 and health < 30:
        light_mode = "steady"
        light_color = "yellow"
    elif round_phase.lower() == "freezetime":
        light_mode = "steady"
        light_color = "blue" if team.upper() == "CT" else "green" if team.upper() == "T" else "white"
    elif round_phase.lower() == "live":
        light_mode = "steady"
        light_color = "blue" if team.upper() == "CT" else "green" if team.upper() == "T" else "off"

    return {
        "mode": light_mode,
        "color": light_color,
        "recommended_color": light_color,
        "blink_interval_ms": blink_interval_ms,
    }


def publish_if_changed(topic_key: str, payload: str, topic: str, retain: bool = True):
    if _last_light_cache.get(topic_key) == payload:
        return
    _last_light_cache[topic_key] = payload
    publish(topic, payload, retain=retain)


def pulse_worker():
    global _bomb_planted_monotonic

    pulse_state = "OFF"
    next_flip = 0.0
    planted_active = False

    publish(f"{BASE}/light/pulse", "OFF", retain=True)

    while True:
        time.sleep(0.03)

        with _state_lock:
            data = dict(_latest_state)

        if not data:
            planted_active = False
            _bomb_planted_monotonic = None
            if pulse_state != "OFF":
                pulse_state = "OFF"
                publish(f"{BASE}/light/pulse", "OFF", retain=True)
            continue

        derived = derive_light_state(data)
        mode = str(derived["mode"])
        color = str(derived["color"])
        recommended_color = str(derived["recommended_color"])
        blink_interval_ms = int(derived["blink_interval_ms"])

        round_bomb = str(deep_get(data, "round", "bomb", default="") or "").lower()
        bomb_state = str(deep_get(data, "bomb", "state", default=round_bomb) or "").lower()
        bomb_countdown = to_float(deep_get(data, "bomb", "countdown", default=0))

        publish_if_changed("mode", mode, f"{BASE}/light/mode", retain=True)
        publish_if_changed("color", color, f"{BASE}/light/color", retain=True)
        publish_if_changed("recommended_color", recommended_color, f"{BASE}/light/recommended_color", retain=True)
        publish_if_changed("blink_interval_ms", str(blink_interval_ms), f"{BASE}/light/blink_interval_ms", retain=True)

        now = time.monotonic()
        planted_now = (bomb_state == "planted" or round_bomb == "planted")

        if planted_now and not planted_active:
            planted_active = True
            _bomb_planted_monotonic = now
            pulse_state = "OFF"
            publish(f"{BASE}/light/pulse", "OFF", retain=True)
            next_flip = now + 0.55

        if not planted_now:
            planted_active = False
            _bomb_planted_monotonic = None

        if mode == "blink" and color == "red" and planted_now:
            if bomb_countdown > 0:
                time_left = bomb_countdown
            elif _bomb_planted_monotonic is not None:
                elapsed = max(0.0, now - _bomb_planted_monotonic)
                time_left = max(0.0, 40.0 - elapsed)
            else:
                time_left = 40.0

            period = calc_visual_period_seconds(time_left)
            on_time = min(0.28, max(0.13, period * 0.45))
            off_time = max(0.06, period - on_time)

            if now >= next_flip:
                if pulse_state == "OFF":
                    pulse_state = "ON"
                    publish(f"{BASE}/light/pulse", "ON", retain=True)
                    next_flip = now + on_time
                else:
                    pulse_state = "OFF"
                    publish(f"{BASE}/light/pulse", "OFF", retain=True)
                    next_flip = now + off_time
        else:
            if pulse_state != "OFF":
                pulse_state = "OFF"
                publish(f"{BASE}/light/pulse", "OFF", retain=True)
            next_flip = now


def ingest_payload(data: dict[str, Any]):
    with _state_lock:
        _latest_state.clear()
        _latest_state.update(data)

    publish(f"{BASE}/state/raw", data, retain=False)

    flat = flatten_to_topics(f"{BASE}/state", data)
    for topic, value in flat.items():
        publish(topic, value, retain=False)
        if OPTIONS.get("publish_discovery", True):
            path = topic[len(f"{BASE}/state/"):] if topic.startswith(f"{BASE}/state/") else topic
            maybe_publish_dynamic_discovery(path, topic)

    round_phase = deep_get(data, "round", "phase", default="")
    round_bomb = deep_get(data, "round", "bomb", default="")
    phase_name = deep_get(data, "map", "phase", default="")
    phase_time_left = to_float(deep_get(data, "phase_countdowns", "phase_ends_in", default=0))
    bomb_state = deep_get(data, "bomb", "state", default=round_bomb)
    bomb_countdown = to_float(deep_get(data, "bomb", "countdown", default=0))

    publish(f"{BASE}/round/phase", round_phase)
    publish(f"{BASE}/round/bomb", round_bomb)
    publish(f"{BASE}/phase/name", phase_name)
    publish(f"{BASE}/phase/time_left", phase_time_left)
    publish(f"{BASE}/bomb/state", bomb_state)
    publish(f"{BASE}/bomb/countdown", bomb_countdown)


@app.post("/")
def ingest_root():
    data = request.get_json(silent=True) or {}
    ingest_payload(data)
    return jsonify({"ok": True})


@app.post("/gsi")
def ingest_gsi():
    data = request.get_json(silent=True) or {}
    ingest_payload(data)
    return jsonify({"ok": True})


if __name__ == "__main__":
    threading.Thread(target=mqtt_loop, daemon=True).start()
    threading.Thread(target=pulse_worker, daemon=True).start()
    print("Starting CS2 GSI Bridge (Python Full State) on port 3001", flush=True)
    app.run(host="0.0.0.0", port=3001)
