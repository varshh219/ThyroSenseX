import os

# ── Detect Raspberry Pi ──────────────────────────────────────
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo", "r") as f:
            return "Raspberry Pi" in f.read()
    except:
        return False

ON_PI     = is_raspberry_pi()
ON_LAPTOP = not ON_PI

# ── Display ─────────────────────────────────────────────────
FULLSCREEN = ON_PI
WINDOW_W   = 480
WINDOW_H   = 680

# ── Paths ───────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(BASE_DIR, "model", "thyroid_model.pkl")
XGB_PATH     = os.path.join(BASE_DIR, "model", "xgb_model.pkl")
CNN_PATH     = os.path.join(BASE_DIR, "model", "cnn_model.h5")
SCALER_PATH  = os.path.join(BASE_DIR, "model", "scaler.pkl")
REPORTS_DIR  = os.path.join(BASE_DIR, "reports", "output")

# ── Sensor flags ────────────────────────────────────────────
SIMULATE_THERMAL = ON_LAPTOP
USE_PI_CAMERA    = ON_PI
USE_OLED         = ON_PI

# ── Audio ───────────────────────────────────────────────────
AUDIO_DURATION   = 4
AUDIO_SAMPLERATE = 22050
