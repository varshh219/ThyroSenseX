import cv2
import numpy as np


def extract_face_features(image_input) -> dict:
    try:
        frame = _to_bgr(image_input)

        if frame is None:
            print("[face_features] Invalid image → zeros")
            return _zeros()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = frame.shape[:2]

        # ── Face detection ─────────────────────────
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

        if len(faces) == 0:
            print("[face_features] No face detected → zeros")
            return _zeros()

        # Largest face
        x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        face_roi = gray[y:y+fh, x:x+fw]
        face_bgr = frame[y:y+fh, x:x+fw]

        # ── Eye detection ─────────────────────────
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )
        eyes = eye_cascade.detectMultiScale(face_roi, 1.1, 4)

        eye_openness = 0.0
        eye_symmetry = 0.0

        if len(eyes) >= 2:
            eyes = sorted(eyes, key=lambda e: e[0])[:2]
            e1h, e2h = eyes[0][3], eyes[1][3]

            eye_openness = float((e1h + e2h) / 2) / max(fh, 1)
            eye_symmetry = 1.0 - abs(e1h - e2h) / max(e1h + e2h, 1)

        elif len(eyes) == 1:
            eye_openness = float(eyes[0][3]) / max(fh, 1)

        # ── Face geometry ─────────────────────────
        face_ratio = float(fw) / max(fh, 1)

        left_half  = face_roi[:, :fw//2]
        right_half = face_roi[:, fw//2:]

        brightness_sym = 1.0 - abs(
            float(left_half.mean()) - float(right_half.mean())
        ) / 255.0

        # ── Neck region ─────────────────────────
        neck_y1 = y + fh
        neck_y2 = min(h, y + fh + fh // 3)
        neck_x1 = x + fw // 4
        neck_x2 = x + 3 * fw // 4

        neck_mean = 0.0
        neck_std  = 0.0

        if neck_y2 > neck_y1 and neck_x2 > neck_x1:
            neck_roi = gray[neck_y1:neck_y2, neck_x1:neck_x2]
            if neck_roi.size > 0:
                neck_mean = float(neck_roi.mean()) / 255.0
                neck_std  = float(np.std(neck_roi)) / 255.0

        # ── Skin tone ─────────────────────────
        b_mean = float(face_bgr[:, :, 0].mean()) / 255.0
        g_mean = float(face_bgr[:, :, 1].mean()) / 255.0
        r_mean = float(face_bgr[:, :, 2].mean()) / 255.0

        # ── Position ─────────────────────────
        face_center_x = float(x + fw / 2) / max(w, 1)
        face_center_y = float(y + fh / 2) / max(h, 1)
        face_area     = float(fw * fh) / max(w * h, 1)

        features = {
            "face_eye_openness":    round(eye_openness, 4),
            "face_eye_symmetry":    round(eye_symmetry, 4),
            "face_ratio":           round(face_ratio, 4),
            "face_brightness_sym":  round(brightness_sym, 4),
            "face_neck_mean":       round(neck_mean, 4),
            "face_neck_std":        round(neck_std, 4),
            "face_skin_b":          round(b_mean, 4),
            "face_skin_g":          round(g_mean, 4),
            "face_skin_r":          round(r_mean, 4),
            "face_center_x":        round(face_center_x, 4),
            "face_center_y":        round(face_center_y, 4),
            "face_area":            round(face_area, 4),
        }

        print(f"[face_features] ✓ {len(features)} features extracted")
        return features

    except Exception as e:
        print(f"[face_features] ERROR: {e}")
        return _zeros()


# ── Helpers ─────────────────────────────

def _to_bgr(image_input):
    if image_input is None:
        return None

    if isinstance(image_input, np.ndarray):
        return image_input

    if isinstance(image_input, (bytes, bytearray)):
        arr = np.frombuffer(image_input, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if isinstance(image_input, str):
        import os
        if os.path.exists(image_input):
            return cv2.imread(image_input)

    return None


def _zeros():
    return {
        "face_eye_openness":    0.0,
        "face_eye_symmetry":    0.0,
        "face_ratio":           1.0,
        "face_brightness_sym":  1.0,
        "face_neck_mean":       0.0,
        "face_neck_std":        0.0,
        "face_skin_b":          0.0,
        "face_skin_g":          0.0,
        "face_skin_r":          0.0,
        "face_center_x":        0.5,
        "face_center_y":        0.5,
        "face_area":            0.0,
    }