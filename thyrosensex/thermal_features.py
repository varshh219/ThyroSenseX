import numpy as np


def extract_thermal_features(data) -> dict:
    try:
        arr = _to_array(data)

        if arr is None:
            print("[thermal_features] Invalid data → zeros")
            return _zeros()

        arr = arr.astype(np.float32)
        flat = arr.flatten()

        # ── Basic stats ─────────────────────
        mean  = float(np.mean(flat))
        std   = float(np.std(flat))
        t_max = float(np.max(flat))
        t_min = float(np.min(flat))
        t_range = t_max - t_min

        # ── Regions ─────────────────────────
        forehead  = float(arr[0:2, :].mean())
        mid_zone  = float(arr[2:5, :].mean())
        chin_neck = float(arr[5:8, :].mean())

        left_mean  = float(arr[:, 0:4].mean())
        right_mean = float(arr[:, 4:8].mean())
        lr_asymmetry = abs(left_mean - right_mean)

        centre = float(arr[3:5, 3:5].mean())

        # ── Hot spots ───────────────────────
        hot_threshold = mean + std
        hot_pixel_count = int(np.sum(flat > hot_threshold))
        hot_ratio = float(hot_pixel_count) / max(len(flat), 1)

        # ── Gradients ───────────────────────
        grad_v = float(np.mean(np.abs(np.diff(arr, axis=0))))
        grad_h = float(np.mean(np.abs(np.diff(arr, axis=1))))

        features = {
            "thermal_mean":         round(mean, 4),
            "thermal_std":          round(std, 4),
            "thermal_max":          round(t_max, 4),
            "thermal_min":          round(t_min, 4),
            "thermal_range":        round(t_range, 4),

            "thermal_forehead":     round(forehead, 4),
            "thermal_mid":          round(mid_zone, 4),
            "thermal_chin_neck":    round(chin_neck, 4),

            "thermal_left_mean":    round(left_mean, 4),
            "thermal_right_mean":   round(right_mean, 4),
            "thermal_lr_asymmetry": round(lr_asymmetry, 4),

            "thermal_centre":       round(centre, 4),
            "thermal_hot_ratio":    round(hot_ratio, 4),

            "thermal_grad_v":       round(grad_v, 4),
            "thermal_grad_h":       round(grad_h, 4),
        }

        print(f"[thermal_features] ✓ {len(features)} features (mean={mean:.1f}°C)")
        return features

    except Exception as e:
        print(f"[thermal_features] ERROR: {e}")
        return _zeros()


# ── Helpers ─────────────────────────

def _to_array(data):
    if data is None:
        return None

    if isinstance(data, np.ndarray):
        if data.size == 64:
            return data.reshape(8, 8)
        return None

    if isinstance(data, (list, tuple)):
        try:
            arr = np.array(data, dtype=np.float32)
            if arr.size == 64:
                return arr.reshape(8, 8)
        except:
            return None

    if isinstance(data, dict):
        grid = data.get("thermal_grid") or data.get("grid")
        if grid:
            return _to_array(grid)

    return None


def _zeros():
    return {
        "thermal_mean":         0.0,
        "thermal_std":          0.0,
        "thermal_max":          0.0,
        "thermal_min":          0.0,
        "thermal_range":        0.0,

        "thermal_forehead":     0.0,
        "thermal_mid":          0.0,
        "thermal_chin_neck":    0.0,

        "thermal_left_mean":    0.0,
        "thermal_right_mean":   0.0,
        "thermal_lr_asymmetry": 0.0,

        "thermal_centre":       0.0,
        "thermal_hot_ratio":    0.0,

        "thermal_grad_v":       0.0,
        "thermal_grad_h":       0.0,
    }