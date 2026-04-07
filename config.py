import os


# ── Detect if running on Raspberry Pi ──────────────────
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo", "r") as f:
            return "Raspberry Pi" in f.read()
    except:
        return False


ON_PI     = is_raspberry_pi()
ON_LAPTOP = not ON_PI

# ── Display ─────────────────────────────────────────────
FULLSCREEN = ON_PI        # fullscreen on Pi, windowed on laptop
WINDOW_W   = 480
WINDOW_H   = 680

# ── Paths ───────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "model", "thyroid_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "output")
ASSETS_DIR  = os.path.join(BASE_DIR, "assets")

# ── Sensor flags ────────────────────────────────────────
SIMULATE_THERMAL = ON_LAPTOP
USE_PI_CAMERA    = ON_PI
USE_OLED         = ON_PI

# ── Audio ───────────────────────────────────────────────
AUDIO_DURATION   = 4
AUDIO_SAMPLERATE = 22050