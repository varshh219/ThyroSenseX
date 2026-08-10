import requests
import numpy as np
import cv2
from config import (
    CAMERA_API, THERMAL_API,
    CAPTURE_API, AUDIO_API,
    BASE_API,
)

DISPLAY_API = f"{BASE_API}/display_result"

# ── Timeouts ─────────────────────────
_T_FRAME   = 20
_T_CAPTURE = 30
_T_AUDIO   = 60
_T_OLED    = 5


# ── Health ───────────────────────────
def check_health():
    try:
        r = requests.get(BASE_API, timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ── Preview APIs ─────────────────────
def get_camera_frame():
    try:
        r = requests.get(CAMERA_API, timeout=_T_FRAME)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        print("[API] Camera preview error:", e)
    return None


def get_thermal_data():
    try:
        r = requests.get(
            f"{BASE_API}/thermal_data",
            timeout=5
        )

        data = r.json()

        if data.get("ok"):
            grid = data.get("grid")  # list of temperature values

            # Convert thermal grid to a visual image
            arr = np.array(grid, dtype=np.float32)

            # If it's a flat list, reshape to 2D (e.g. 24x32 for MLX90640)
            if arr.ndim == 1:
                arr = arr.reshape(24, 32)  # adjust if your sensor is different

            # Normalize to 0-255
            arr -= arr.min()
            arr /= arr.max() if arr.max() != 0 else 1
            arr = (arr * 255).astype(np.uint8)

            # Apply color map to make it look thermal
            colored = cv2.applyColorMap(arr, cv2.COLORMAP_INFERNO)

            # Encode to JPEG bytes
            _, jpeg = cv2.imencode(".jpg", colored)
            return jpeg.tobytes()  # ✅ returns bytes

    except Exception as e:
        print("[API] Thermal data error:", e)

    return None


# ── Capture APIs ─────────────────────
def capture_image():
    try:
        r = requests.post(CAPTURE_API, timeout=_T_CAPTURE)
        r.raise_for_status()
        data = r.json()

        print("[API] Image captured:", data)
        return data

    except Exception as e:
        raise RuntimeError(f"capture_image failed: {e}")


def record_audio():
    try:
        r = requests.post(AUDIO_API, timeout=_T_AUDIO)
        r.raise_for_status()
        data = r.json()

        print("[API] Audio recorded:", data)
        return data

    except Exception as e:
        raise RuntimeError(f"record_audio failed: {e}")


# ── OLED ─────────────────────────────
def display_result(prediction, confidence):
    try:
        r = requests.post(
            DISPLAY_API,
            json={
                "prediction": prediction,
                "confidence": confidence
            },
            timeout=_T_OLED
        )

        if r.status_code == 200:
            print("[API] OLED updated")
            return True

    except Exception as e:
        print("[API] OLED error:", e)

    return False