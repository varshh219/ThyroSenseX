import cv2
import numpy as np
import mediapipe as mp

# ── INIT MEDIAPIPE (LOAD ONCE) ───────────
mp_face = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True
)


# ─────────────────────────────────────────
# MAIN RAW FEATURE EXTRACTOR
# ─────────────────────────────────────────
def extract_face_raw(image_input):
    try:
        frame = _to_bgr(image_input)

        if frame is None:
            print("[face_raw] Invalid image")
            return {}

        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = mp_face.process(rgb)

        if not result.multi_face_landmarks:
            print("[face_raw] No face detected")
            return {}

        lm = result.multi_face_landmarks[0].landmark

        def pt(i):
            return int(lm[i].x * w), int(lm[i].y * h)

        # ── EYES ─────────────────────────
        le_h = abs(pt(159)[1] - pt(145)[1])
        re_h = abs(pt(386)[1] - pt(374)[1])

        le_w = abs(pt(33)[0] - pt(133)[0])
        re_w = abs(pt(362)[0] - pt(263)[0])

        eye_openness = (le_h + re_h) / (le_w + re_w + 1e-5)
        eye_symmetry = 1.0 - abs(le_h - re_h) / (le_h + re_h + 1e-5)

        # ── FACE GEOMETRY ────────────────
        chin = pt(152)
        forehead = pt(10)
        left_face = pt(234)
        right_face = pt(454)

        y1, y2 = sorted([forehead[1], chin[1]])
        x1, x2 = sorted([left_face[0], right_face[0]])

        y1 = max(0, y1)
        y2 = min(h, y2)
        x1 = max(0, x1)
        x2 = min(w, x2)

        face_height = max(1, y2 - y1)
        face_width = max(1, x2 - x1)

        face_area = (face_width * face_height) / (w * h + 1e-5)

        face_roi = frame[y1:y2, x1:x2]

        # ── SKIN + SYMMETRY ──────────────
        if face_roi.size > 0:
            blur = cv2.GaussianBlur(face_roi, (5, 5), 0)

            b_mean = np.mean(blur[:, :, 0]) / 255.0
            g_mean = np.mean(blur[:, :, 1]) / 255.0
            r_mean = np.mean(blur[:, :, 2]) / 255.0

            mid = face_roi.shape[1] // 2
            left = face_roi[:, :mid]
            right = cv2.flip(face_roi[:, mid:], 1)

            if left.shape == right.shape and left.size > 0:
                diff = np.mean(np.abs(left.astype(float) - right.astype(float)))
                brightness_sym = 1.0 - (diff / 255.0)
            else:
                brightness_sym = 1.0
        else:
            b_mean = g_mean = r_mean = 0.0
            brightness_sym = 1.0

        # ── NECK REGION ──────────────────
        neck_y1 = y2
        neck_y2 = min(h, y2 + face_height // 2)

        neck = frame[neck_y1:neck_y2, x1:x2]

        if neck.size > 0:
            neck_gray = cv2.cvtColor(neck, cv2.COLOR_BGR2GRAY)
            neck_mean = np.mean(neck_gray) / 255.0
            neck_std = np.std(neck_gray) / 255.0
        else:
            neck_mean = neck_std = 0.0

        return {
            "face_eye_openness": float(eye_openness),
            "face_eye_symmetry": float(eye_symmetry),
            "face_skin_r": float(r_mean),
            "face_skin_g": float(g_mean),
            "face_skin_b": float(b_mean),
            "face_neck_mean": float(neck_mean),
            "face_neck_std": float(neck_std),
            "face_brightness_sym": float(brightness_sym),
            "face_area": float(face_area),
        }

    except Exception as e:
        print("[face_raw] ERROR:", e)
        return {}


# ─────────────────────────────────────────
# IMAGE LOADER
# ─────────────────────────────────────────
def _to_bgr(image_input):
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