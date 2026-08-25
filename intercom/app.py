import json
import os
import re
import subprocess
import threading
import time
import uuid
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__)

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
AUDIO_DIR = DATA_DIR / "audio"
CONFIG_FILE = DATA_DIR / "announcements.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
RECEIVER_URL = os.environ.get("RECEIVER_URL", "http://127.0.0.1/request.cgi")
INTERCOM_INPUT = os.environ.get("INTERCOM_INPUT", "sat")
PULSE_SINK = os.environ.get("PULSE_SINK", "alsa_output.pci-0000_0c_00.1.hdmi-stereo-extra1")

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
play_lock = threading.Lock()
live_lock = threading.Lock()
live_session = {"id": None, "proc": None, "previous_main": None}


def load_settings():
    settings = {"announcement_volume": 70}
    if SETTINGS_FILE.exists():
        try:
            saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                settings.update(saved)
        except Exception:
            pass
    return settings

def save_settings(settings):
    tmp = SETTINGS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    tmp.replace(SETTINGS_FILE)

def load_items():
    if not CONFIG_FILE.exists():
        return []
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_items(items):
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(items, indent=2), encoding="utf-8")
    tmp.replace(CONFIG_FILE)

def slugify(value):
    value = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-").lower()
    return value or uuid.uuid4().hex[:10]

def convert_to_wav(source, wav):
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", str(source),
            "-vn", "-ac", "2", "-ar", "44100",
            "-c:a", "pcm_s16le", str(wav)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        wav.unlink(missing_ok=True)
        detail = e.stderr.decode("utf-8", errors="ignore")[-800:]
        raise RuntimeError("Could not decode audio file: " + detail)


def receiver_set(feature, value):
    body = {
        "type": "http_set",
        "packet": [{"id": int(time.time()*1000) % 999, "feature": feature, "value": value}],
    }
    r = requests.post(RECEIVER_URL, json=body, timeout=4)
    if r.status_code not in (200, 519):
        r.raise_for_status()

def receiver_get(feature):
    body = {
        "type": "http_get",
        "packet": [{"id": int(time.time()*1000) % 999, "feature": feature}],
    }
    r = requests.post(RECEIVER_URL, json=body, timeout=4)
    r.raise_for_status()
    data = r.json()
    packet = data.get("packet") or []
    return packet[0].get("value") if packet else None

def normalize_main_input(value):
    v = str(value or "").lower()
    compact = re.sub(r"[^a-z0-9]", "", v)
    if "bddvd" in compact or compact in ("bd", "dvd"):
        return "bddvd"
    if "sat" in compact or "catv" in compact:
        return "sat"
    if "game" in compact:
        return "game"
    if "video" in compact:
        return "video"
    if "aux" in compact:
        return "aux"
    if compact == "tv" or "tvaudio" in compact:
        return "tv"
    return None


MAIN_INPUT_FEATURES = {
    "tv": "GUI.tv",
    "bddvd": "GUI.bddvd",
    "game": "GUI.game",
    "sat": "GUI.sat",
    "video": "GUI.video",
    "aux": "GUI.aux",
}


def set_main_input(input_key):
    feature = MAIN_INPUT_FEATURES.get(input_key)
    if not feature:
        raise RuntimeError(f"Unsupported main input: {input_key}")
    receiver_set(feature, "main")


def wait_for_main_input(input_key, timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if normalize_main_input(receiver_get("main.input")) == input_key:
                return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


def prepare_intercom_route():
    previous_raw = receiver_get("main.input")
    previous_key = normalize_main_input(previous_raw)

    # The ZA1100ES only passes the UGREEN HDMI audio through to the Zone 2
    # analog output when the MAIN zone is also physically on SAT/CATV.
    if previous_key != "sat":
        set_main_input("sat")
        if not wait_for_main_input("sat"):
            raise RuntimeError("Receiver main zone did not switch to SAT/CATV")

    zone2_prepare()
    return previous_key


def restore_main_input(previous_key):
    if not previous_key or previous_key == "sat":
        return
    try:
        set_main_input(previous_key)
        wait_for_main_input(previous_key)
    except Exception:
        app.logger.exception("Unable to restore previous main-zone input")


def zone2_prepare():
    receiver_set("zone2.power", "on")

    # Wait for Zone 2 to actually report ON.
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            if receiver_get("zone2.power") == "on":
                break
        except Exception:
            pass
        time.sleep(0.25)

    receiver_set("zone2.input", INTERCOM_INPUT)

    # Wait for the receiver to confirm SAT/CATV routing before audio starts.
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            if receiver_get("zone2.input") == INTERCOM_INPUT:
                break
        except Exception:
            pass
        time.sleep(0.25)

    # HDMI/Zone 2 analog output needs a moment to lock after the route changes.
    time.sleep(2.0)

def zone2_off():
    try:
        receiver_set("zone2.power", "off")
    except Exception:
        app.logger.exception("Unable to turn Zone 2 off")

def play_wav(path):
    percent = max(0, min(100, int(load_settings().get("announcement_volume", 70))))
    pulse_volume = round(65536 * percent / 100)
    subprocess.run(["paplay", f"--device={PULSE_SINK}", f"--volume={pulse_volume}", str(path)], check=True)

def whole_house_play(item_id):
    with play_lock:
        items = load_items()
        item = next((x for x in items if x.get("id") == item_id), None)
        if not item:
            raise RuntimeError("Announcement not found")
        wav = AUDIO_DIR / item["audio"]
        if not wav.exists():
            raise RuntimeError("Audio file is missing")
        previous_main = prepare_intercom_route()
        try:
            # Keep MAIN SAT/CATV, Zone 2, and the HDMI route active while
            # the announcement plays three consecutive times.
            for play_number in range(3):
                play_wav(wav)
                if play_number < 2:
                    time.sleep(0.35)

            # Let the last audio samples clear the HDMI/Zone 2 path before shutdown.
            time.sleep(1.0)
        finally:
            zone2_off()
            restore_main_input(previous_main)


@app.after_request
def add_cors_headers(response):
    # The Sony LAN remote is served from the same NAS on port 8088.
    # Allow it to call this intercom service on port 8089.
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def stop_live_session():
    with live_lock:
        proc = live_session.get("proc")
        previous_main = live_session.get("previous_main")
        live_session["proc"] = None
        live_session["id"] = None
        live_session["previous_main"] = None
    if proc:
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass
    zone2_off()
    restore_main_input(previous_main)


def start_live_session(sample_rate):
    stop_live_session()
    previous_main = prepare_intercom_route()

    settings = load_settings() if "load_settings" in globals() else {"announcement_volume": 70}
    percent = max(0, min(100, int(settings.get("announcement_volume", 70))))
    pulse_volume = round(65536 * percent / 100)

    session_id = uuid.uuid4().hex
    cmd = [
        "paplay",
        f"--device={PULSE_SINK}",
        "--raw",
        "--format=s16le",
        f"--rate={sample_rate}",
        "--channels=1",
        f"--volume={pulse_volume}",
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with live_lock:
        live_session["id"] = session_id
        live_session["proc"] = proc
        live_session["previous_main"] = previous_main
    return session_id

@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/live/start")
def live_start():
    payload = request.get_json(silent=True) or {}
    try:
        sample_rate = int(payload.get("sample_rate", 48000))
    except (TypeError, ValueError):
        sample_rate = 48000
    sample_rate = max(8000, min(96000, sample_rate))

    try:
        session_id = start_live_session(sample_rate)
        return jsonify(ok=True, session_id=session_id, sample_rate=sample_rate)
    except Exception as e:
        app.logger.exception("Unable to start live intercom")
        try:
            stop_live_session()
        except Exception:
            pass
        return jsonify(error=str(e)), 500


@app.post("/api/live/<session_id>/audio")
def live_audio(session_id):
    data = request.get_data(cache=False)
    if not data:
        return jsonify(ok=True)

    with live_lock:
        if live_session.get("id") != session_id or not live_session.get("proc"):
            return jsonify(error="Live session not active"), 409
        proc = live_session["proc"]
        try:
            proc.stdin.write(data)
            proc.stdin.flush()
        except Exception as e:
            return jsonify(error=str(e)), 500

    return jsonify(ok=True)


@app.post("/api/live/<session_id>/stop")
def live_stop(session_id):
    with live_lock:
        active = live_session.get("id")
    if active and active != session_id:
        return jsonify(error="Live session mismatch"), 409
    try:
        stop_live_session()
        return jsonify(ok=True)
    except Exception as e:
        app.logger.exception("Unable to stop live intercom")
        return jsonify(error=str(e)), 500


@app.get("/api/live/status")
def live_status():
    with live_lock:
        proc = live_session.get("proc")
        session_id = live_session.get("id")
        active = bool(proc and proc.poll() is None)
    return jsonify(active=active, session_id=session_id if active else None)

@app.get("/api/settings")
def get_settings():
    return jsonify(load_settings())

@app.post("/api/settings")
def update_settings():
    payload = request.get_json(silent=True) or {}
    try:
        value = max(0, min(100, int(payload.get("announcement_volume", 70))))
    except (TypeError, ValueError):
        return jsonify(error="Invalid volume"), 400
    settings = load_settings()
    settings["announcement_volume"] = value
    save_settings(settings)
    return jsonify(settings)

@app.get("/api/announcements")
def announcements():
    return jsonify(load_items())

@app.post("/api/announcements")
def create_announcement():
    label = (request.form.get("label") or "").strip().upper()
    upload = request.files.get("audio")
    if not label:
        return jsonify(error="Button name is required"), 400
    if not upload or not upload.filename:
        return jsonify(error="Audio file is required"), 400

    item_id = uuid.uuid4().hex
    base = f"{slugify(label)}-{item_id[:8]}"
    source = AUDIO_DIR / f"{base}.source"
    wav = AUDIO_DIR / f"{base}.wav"
    upload.save(source)

    try:
        convert_to_wav(source, wav)
    except RuntimeError as e:
        return jsonify(error=str(e)), 400
    finally:
        source.unlink(missing_ok=True)

    items = load_items()
    order = max([x.get("order",0) for x in items], default=0) + 1
    item = {"id":item_id,"label":label,"audio":wav.name,"enabled":True,"order":order}
    items.append(item)
    save_items(items)
    return jsonify(item), 201

@app.post("/api/announcements/<item_id>/audio")
def replace_audio(item_id):
    items = load_items()
    item = next((x for x in items if x.get("id") == item_id), None)
    if not item:
        return jsonify(error="Not found"), 404

    upload = request.files.get("audio")
    if not upload or not upload.filename:
        return jsonify(error="Audio file is required"), 400

    base = f"{slugify(item['label'])}-{item_id[:8]}"
    source = AUDIO_DIR / f"{base}.replacement"
    wav = AUDIO_DIR / f"{base}.wav"
    upload.save(source)

    try:
        convert_to_wav(source, wav)
    except RuntimeError as e:
        return jsonify(error=str(e)), 400
    finally:
        source.unlink(missing_ok=True)

    old_audio = item.get("audio")
    item["audio"] = wav.name
    save_items(items)
    if old_audio and old_audio != wav.name:
        (AUDIO_DIR / old_audio).unlink(missing_ok=True)
    return jsonify(item)

@app.post("/api/announcements/<item_id>/toggle")
def toggle(item_id):
    items = load_items()
    item = next((x for x in items if x.get("id")==item_id), None)
    if not item:
        return jsonify(error="Not found"), 404
    item["enabled"] = not bool(item.get("enabled", True))
    save_items(items)
    return jsonify(item)

@app.delete("/api/announcements/<item_id>")
def delete(item_id):
    items = load_items()
    item = next((x for x in items if x.get("id")==item_id), None)
    if not item:
        return jsonify(error="Not found"), 404
    (AUDIO_DIR / item.get("audio","")).unlink(missing_ok=True)
    save_items([x for x in items if x.get("id") != item_id])
    return jsonify(ok=True)

@app.post("/api/announcements/<item_id>/play")
def play(item_id):
    try:
        whole_house_play(item_id)
        return jsonify(ok=True)
    except Exception as e:
        app.logger.exception("Intercom playback failed")
        return jsonify(error=str(e)), 500

@app.get("/api/announcements/<item_id>/audio")
def audio(item_id):
    items = load_items()
    item = next((x for x in items if x.get("id")==item_id), None)
    if not item:
        return jsonify(error="Not found"), 404
    return send_from_directory(AUDIO_DIR, item["audio"], mimetype="audio/wav")

@app.get("/api/enabled")
def enabled():
    items = [x for x in load_items() if x.get("enabled", True)]
    items.sort(key=lambda x:x.get("order",0))
    return jsonify([{"id":x["id"],"label":x["label"]} for x in items])

@app.get("/api/receiver-power")
def receiver_power():
    try:
        value = receiver_get("main.power")
        return jsonify(ok=True, power=value)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@app.post("/api/receiver-power/toggle")
def receiver_power_toggle():
    try:
        current = receiver_get("main.power")
        if current == "on":
            # Use the same proven GUI power behavior as the Sony remote.
            receiver_set("GUI.power", "main")
            target = "off"
        else:
            receiver_set("main.power", "on")
            target = "on"

        deadline = time.time() + 8
        observed = current
        while time.time() < deadline:
            time.sleep(0.4)
            try:
                observed = receiver_get("main.power")
                if observed == target:
                    break
            except Exception:
                pass

        return jsonify(ok=True, power=observed, requested=target)
    except Exception as e:
        app.logger.exception("Receiver power toggle failed")
        return jsonify(ok=False, error=str(e)), 500

@app.get("/api/health")
def health():
    return jsonify(ok=True, receiver=RECEIVER_URL, sink=PULSE_SINK)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8089, threaded=True)
