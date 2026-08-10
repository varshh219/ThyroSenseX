import numpy as np
import io
import os


# ─────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────
def extract_voice_features(audio_input) -> dict:

    try:
        import librosa

        # ── LOAD AUDIO ───────────────────
        y, sr = _load_audio(audio_input)

        print("\n=== VOICE DEBUG ===")
        print("Audio input type:", type(audio_input))
        print("Sample rate:", sr)

        if y is not None:
            print("Audio shape:", y.shape)
            print("Audio length:", len(y))
            print("Audio duration:", round(len(y) / sr, 2), "seconds")

        # ── INVALID AUDIO ─────────────────
        if y is None:
            print("[voice_features] Audio loading failed")
            return _zeros()

        if len(y) == 0:
            print("[voice_features] Empty audio")
            return _zeros()

        # ── REMOVE SILENCE ───────────────
        y, _ = librosa.effects.trim(y, top_db=20)

        if len(y) == 0:
            print("[voice_features] Silent audio")
            return _zeros()

        # ── TOO SHORT CHECK ──────────────
        if len(y) < sr * 0.5:
            print("[voice_features] Audio too short")
            return _zeros()

        # ── NORMALIZE AUDIO ──────────────
        max_amp = np.max(np.abs(y))

        if max_amp < 1e-6:
            print("[voice_features] Near-silent recording")
            return _zeros()

        y = y / max_amp

        # ── PITCH EXTRACTION ─────────────
        f0, voiced_flag, _ = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr,
        )

        voiced_f0 = np.array([])

        if f0 is not None and voiced_flag is not None:
            voiced_f0 = f0[voiced_flag]
            voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]

        # ── REMOVE OUTLIERS ──────────────
        if len(voiced_f0) > 0:

            median = np.median(voiced_f0)
            std = np.std(voiced_f0) + 1e-5

            voiced_f0 = voiced_f0[
                np.abs(voiced_f0 - median) < 2 * std
            ]

        # ── PITCH FEATURES ───────────────
        if len(voiced_f0) > 0:

            pitch_mean = float(np.mean(voiced_f0))
            pitch_std = float(np.std(voiced_f0))
            pitch_min = float(np.min(voiced_f0))
            pitch_max = float(np.max(voiced_f0))

        else:

            pitch_mean = 0.0
            pitch_std = 0.0
            pitch_min = 0.0
            pitch_max = 0.0

        # ── ENERGY ───────────────────────
        rms = librosa.feature.rms(y=y)[0]

        energy_mean = float(np.mean(rms))
        energy_std = float(np.std(rms))

        # ── ZERO CROSSING RATE ───────────
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        zcr_mean = float(np.mean(zcr))

        # ── MFCC FEATURES ────────────────
        mfccs = librosa.feature.mfcc(
            y=y,
            sr=sr,
            n_mfcc=13
        )

        mfcc_mean_1 = (
            float(np.mean(mfccs[0]))
            if mfccs.shape[0] > 0 else 0.0
        )

        mfcc_mean_2 = (
            float(np.mean(mfccs[1]))
            if mfccs.shape[0] > 1 else 0.0
        )

        mfcc_mean_3 = (
            float(np.mean(mfccs[2]))
            if mfccs.shape[0] > 2 else 0.0
        )

        # ── SAFE CLAMP ───────────────────
        def clamp(x):
            return float(np.clip(x, 0, 1000))

        # ── FINAL FEATURES ───────────────
        features = {

            "pitch_mean": round(clamp(pitch_mean), 4),
            "pitch_std": round(clamp(pitch_std), 4),
            "pitch_min": round(clamp(pitch_min), 4),
            "pitch_max": round(clamp(pitch_max), 4),

            "energy_mean": round(clamp(energy_mean), 4),
            "energy_std": round(clamp(energy_std), 4),

            "zcr_mean": round(clamp(zcr_mean), 4),

            "mfcc_mean_1": round(clamp(mfcc_mean_1), 4),
            "mfcc_mean_2": round(clamp(mfcc_mean_2), 4),
            "mfcc_mean_3": round(clamp(mfcc_mean_3), 4),
        }

        print("\n=== VOICE FEATURES ===")

        for k, v in features.items():
            print(k, ":", v)

        print(
            f"\n[voice_features] ✓ {len(features)} features"
        )

        return features

    except ImportError:
        print("[voice_features] ERROR: install librosa + soundfile")
        return _zeros()

    except Exception as e:
        print("[voice_features] ERROR:", e)
        return _zeros()


# ─────────────────────────────────────────
# AUDIO LOADER
# ─────────────────────────────────────────
def _load_audio(audio_input):

    try:
        import librosa
        import soundfile as sf

        # ── CASE 1: BYTES ─────────────────
        if isinstance(audio_input, (bytes, bytearray)):

            print("Loading from bytes...")

            buf = io.BytesIO(audio_input)

            y, sr = sf.read(
                buf,
                dtype="float32"
            )

            if y is None or len(y) == 0:
                print("Byte audio empty")
                return None, 22050

            # Stereo → mono
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)

            return y, sr

        # ── CASE 2: FILE PATH ────────────
        if isinstance(audio_input, str):

            print("Received audio path:", audio_input)

            abs_path = os.path.abspath(audio_input)

            print("Absolute path:", abs_path)

            if not os.path.exists(audio_input):
                print("[voice_features] FILE NOT FOUND")
                return None, 22050

            file_size = os.path.getsize(audio_input)

            print("Audio file size:", file_size, "bytes")

            if file_size == 0:
                print("[voice_features] Empty WAV file")
                return None, 22050

            y, sr = librosa.load(
                audio_input,
                sr=None,
                mono=True
            )

            print("Loaded audio successfully")
            print("Samples:", len(y))
            print("Duration:", round(len(y) / sr, 2), "seconds")

            return y, sr

    except Exception as e:
        print("[voice_features] Load error:", e)

    return None, 22050


# ─────────────────────────────────────────
# SAFE DEFAULT FEATURES
# ─────────────────────────────────────────
def _zeros():

    return {

        "pitch_mean": 0.0,
        "pitch_std": 0.0,
        "pitch_min": 0.0,
        "pitch_max": 0.0,

        "energy_mean": 0.0,
        "energy_std": 0.0,

        "zcr_mean": 0.0,

        "mfcc_mean_1": 0.0,
        "mfcc_mean_2": 0.0,
        "mfcc_mean_3": 0.0,
    }