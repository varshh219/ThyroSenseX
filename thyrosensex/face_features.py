def extract_face_features(image_input):
    try:
        from thyrosensex.face_raw import extract_face_raw

        raw = extract_face_raw(image_input)

        if not raw:
            print("[face_features] No raw features → zeros")
            return _zeros()

        features = {
            "has_dark_circle": int(raw["face_skin_r"] < 0.4),

            "facial_swelling": int(raw["face_brightness_sym"] < 0.85),

            "puffy_eyes": int(raw["face_eye_openness"] < 0.25),

            "dry_skin_visible": int(
                abs(raw["face_skin_r"] - raw["face_skin_g"]) < 0.05
            ),

            "goiter_visible": int(raw["face_neck_mean"] > 0.6),

            "coarse_facial_features": int(raw["face_neck_std"] > 0.15),

            "tired_expression": int(raw["face_eye_openness"] < 0.2),

            "hair_loss": int(raw["face_area"] < 0.15),

            "weight_gain": 0,  # placeholder

            "pale_skin": int(raw["face_skin_r"] < 0.35),
        }

        print(f"[face_features] ✓ {len(features)} features")
        return features

    except Exception as e:
        print("[face_features] ERROR:", e)
        return _zeros()


# ─────────────────────────────────────────
# DEFAULT SAFE FEATURES
# ─────────────────────────────────────────
def _zeros():
    return {
        "has_dark_circle": 0,
        "facial_swelling": 0,
        "puffy_eyes": 0,
        "dry_skin_visible": 0,
        "goiter_visible": 0,
        "coarse_facial_features": 0,
        "tired_expression": 0,
        "hair_loss": 0,
        "weight_gain": 0,
        "pale_skin": 0,
    }