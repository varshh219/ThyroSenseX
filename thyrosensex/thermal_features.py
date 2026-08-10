import numpy as np
import cv2
import json


# ─────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────
def extract_thermal_features(data) -> dict:
    try:
        print("\n[thermal_features] Raw input type:", type(data))
        print("[thermal_features] RAW DATA =", data)

        arr = _to_array(data)

        if arr is None:
            print("[thermal_features] Invalid input → zeros")
            return _zeros()

        print("[thermal_features] Array shape:", arr.shape)

        arr = arr.astype(np.float32)

        # ── SMOOTHING ────────────────────
        arr = cv2.GaussianBlur(arr, (3, 3), 0)

        flat = arr.flatten()

        # ── BASIC STATS ─────────────────
        t_mean = float(np.mean(flat))
        t_std = float(np.std(flat))
        t_max = float(np.max(flat))
        t_min = float(np.min(flat))
        t_range = t_max - t_min

        # ── REGIONS ─────────────────────
        h, w = arr.shape

        forehead = float(arr[0:h//4, :].mean())
        mid_zone = float(arr[h//4:3*h//4, :].mean())
        chin_neck = float(arr[3*h//4:h, :].mean())

        left_mean = float(arr[:, :w//2].mean())
        right_mean = float(arr[:, w//2:].mean())

        lr_asymmetry = abs(left_mean - right_mean)

        centre = float(arr[h//3:2*h//3, w//3:2*w//3].mean())

        # ── HOTSPOTS ────────────────────
        hot_threshold = t_mean + (1.5 * t_std)
        hot_ratio = float(np.sum(flat > hot_threshold)) / len(flat)

        # ── GRADIENTS ───────────────────
        grad_v = float(np.mean(np.abs(np.diff(arr, axis=0))))
        grad_h = float(np.mean(np.abs(np.diff(arr, axis=1))))

        # ── SAFE CLAMP ──────────────────
        def clamp(x):
            return float(np.clip(x, 0, 50))

        features = {
            "thermal_mean": round(clamp(t_mean), 4),
            "thermal_std": round(clamp(t_std), 4),
            "thermal_max": round(clamp(t_max), 4),
            "thermal_min": round(clamp(t_min), 4),
            "thermal_range": round(clamp(t_range), 4),

            "thermal_forehead": round(clamp(forehead), 4),
            "thermal_mid": round(clamp(mid_zone), 4),
            "thermal_chin_neck": round(clamp(chin_neck), 4),

            "thermal_left_mean": round(clamp(left_mean), 4),
            "thermal_right_mean": round(clamp(right_mean), 4),
            "thermal_lr_asymmetry": round(clamp(lr_asymmetry), 4),

            "thermal_centre": round(clamp(centre), 4),
            "thermal_hot_ratio": round(np.clip(hot_ratio, 0, 1), 4),

            "thermal_grad_v": round(clamp(grad_v), 4),
            "thermal_grad_h": round(clamp(grad_h), 4),
        }

        print(f"[thermal_features] ✓ {len(features)} features extracted")
        print("[thermal_features] Mean Temp =", t_mean)

        return features

    except Exception as e:
        print("[thermal_features] ERROR:", e)
        return _zeros()


# ─────────────────────────────────────────
# INPUT PARSER
# ─────────────────────────────────────────
def _to_array(data):

    try:
        print("[_to_array] type =", type(data))

        # ── CASE 1: numpy array ──────────
        if isinstance(data, np.ndarray):

            print("[_to_array] ndarray size =", data.size)

            if data.size == 64:
                print("[_to_array] Detected 8x8 thermal grid")
                return data.reshape(8, 8)

            elif data.size == 768:
                print("[_to_array] Detected MLX90640 24x32 grid")
                return data.reshape(24, 32)

        # ── CASE 2: list or tuple ────────
        if isinstance(data, (list, tuple)):

            arr = np.array(data, dtype=np.float32)

            print("[_to_array] list/tuple size =", arr.size)

            if arr.size == 64:
                print("[_to_array] Detected 8x8 thermal grid")
                return arr.reshape(8, 8)

            elif arr.size == 768:
                print("[_to_array] Detected MLX90640 24x32 grid")
                return arr.reshape(24, 32)

        # ── CASE 3: dict from API ────────
        if isinstance(data, dict):

            print("[_to_array] dict keys =", data.keys())

            grid = (
                data.get("thermal_grid")
                or data.get("grid")
                or data.get("thermal_frame")
                or data.get("pixels")
            )

            if grid is not None:
                return _to_array(grid)

        # ── CASE 4: JSON string ──────────
        if isinstance(data, str):

            try:
                parsed = json.loads(data)
                return _to_array(parsed)

            except Exception as e:
                print("[_to_array] JSON parse failed:", e)
                return None

    except Exception as e:
        print("[thermal_features] parse error:", e)

    return None


# ─────────────────────────────────────────
# DEFAULT SAFE FEATURES
# ─────────────────────────────────────────
def _zeros():

    return {
        "thermal_mean": 0.0,
        "thermal_std": 0.0,
        "thermal_max": 0.0,
        "thermal_min": 0.0,
        "thermal_range": 0.0,

        "thermal_forehead": 0.0,
        "thermal_mid": 0.0,
        "thermal_chin_neck": 0.0,

        "thermal_left_mean": 0.0,
        "thermal_right_mean": 0.0,
        "thermal_lr_asymmetry": 0.0,

        "thermal_centre": 0.0,
        "thermal_hot_ratio": 0.0,

        "thermal_grad_v": 0.0,
        "thermal_grad_h": 0.0,
    }