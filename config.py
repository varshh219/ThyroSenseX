import os

# ── MODE (MANUAL CONTROL) ────────────────────────────
# Set this manually instead of auto detection
RUN_ON_PI = False   # 👉 True if running on Raspberry Pi

# ── DISPLAY ─────────────────────────────────────────
FULLSCREEN = RUN_ON_PI
WINDOW_W   = 480
WINDOW_H   = 680

# ── PATHS ───────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, "model")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "output")

MODEL_PATH  = os.path.join(MODEL_DIR, "thyroid_model.pkl")
XGB_PATH    = os.path.join(MODEL_DIR, "xgb_model.pkl")
CNN_PATH    = os.path.join(MODEL_DIR, "cnn_model.h5")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

# ── API CONFIG ──────────────────────────────────────
PI_IP = "10.204.204.198"   # 🔁 FILL IN your Pi's full IP  e.g. "10.0.0.42"
PORT  = 5000

BASE_API = f"http://{PI_IP}:{PORT}"

# ── Endpoints ───────────────────────────────────────
CAMERA_API   = f"{BASE_API}/camera_frame"    # GET  → live JPEG frame
THERMAL_API  = f"{BASE_API}/thermal_frame"   # GET  → smooth thermal JPEG
CAPTURE_API  = f"{BASE_API}/capture_image"   # POST → saves image, returns JSON
AUDIO_API    = f"{BASE_API}/record_audio"    # POST → records WAV, returns JSON
SCAN_API     = f"{BASE_API}/scan_face"       # POST → full pipeline, returns result JSON
HEALTH_API   = f"{BASE_API}/health"          # GET  → server alive check

# ── SENSOR FLAGS ────────────────────────────────────
SIMULATE_THERMAL = not RUN_ON_PI
USE_PI_CAMERA    = RUN_ON_PI
USE_OLED         = RUN_ON_PI

# ── AUDIO ───────────────────────────────────────────
AUDIO_DURATION   = 4
AUDIO_SAMPLERATE = 22050

# ── DEBUG ───────────────────────────────────────────
print(f"[CONFIG] Running on : {'Raspberry Pi' if RUN_ON_PI else 'Laptop'}")
print(f"[CONFIG] API BASE   : {BASE_API}")