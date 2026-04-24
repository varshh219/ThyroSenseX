import numpy as np
import io


def extract_voice_features(audio_input) -> dict:
    try:
        import librosa

        # ── Load audio ─────────────────────
        y, sr = _load_audio(audio_input)

        if y is None or len(y) == 0:
            print("[voice_features] Invalid audio → zeros")
            return _zeros()

        # Trim silence
        y, _ = librosa.effects.trim(y, top_db=20)

        if len(y) < sr * 0.5:
            print("[voice_features] Too short → zeros")
            return _zeros()

        # ── Pitch (F0) ─────────────────────
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

        if len(voiced_f0) > 0:
            pitch_mean = float(np.mean(voiced_f0))
            pitch_std  = float(np.std(voiced_f0))
            pitch_min  = float(np.min(voiced_f0))
            pitch_max  = float(np.max(voiced_f0))
        else:
            pitch_mean = pitch_std = pitch_min = pitch_max = 0.0

        # ── Energy ─────────────────────────
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = float(np.mean(rms))
        energy_std  = float(np.std(rms))

        # ── ZCR ────────────────────────────
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        zcr_mean = float(np.mean(zcr))

        # ── MFCC ───────────────────────────
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        mfcc_mean_1 = float(np.mean(mfccs[0])) if mfccs.shape[0] > 0 else 0.0
        mfcc_mean_2 = float(np.mean(mfccs[1])) if mfccs.shape[0] > 1 else 0.0
        mfcc_mean_3 = float(np.mean(mfccs[2])) if mfccs.shape[0] > 2 else 0.0

        features = {
            "pitch_mean":   round(pitch_mean, 4),
            "pitch_std":    round(pitch_std, 4),
            "pitch_min":    round(pitch_min, 4),
            "pitch_max":    round(pitch_max, 4),

            "energy_mean":  round(energy_mean, 4),
            "energy_std":   round(energy_std, 4),

            "zcr_mean":     round(zcr_mean, 4),

            "mfcc_mean_1":  round(mfcc_mean_1, 4),
            "mfcc_mean_2":  round(mfcc_mean_2, 4),
            "mfcc_mean_3":  round(mfcc_mean_3, 4),
        }

        print(f"[voice_features] ✓ {len(features)} features")
        return features

    except ImportError:
        print("[voice_features] librosa missing → pip install librosa")
        return _zeros()

    except Exception as e:
        print(f"[voice_features] ERROR: {e}")
        return _zeros()


# ── Helpers ─────────────────────────

def _load_audio(audio_input):
    try:
        import librosa
        import soundfile as sf

        if isinstance(audio_input, (bytes, bytearray)):
            buf = io.BytesIO(audio_input)
            y, sr = sf.read(buf, dtype="float32")

            if y is None or len(y) == 0:
                return None, sr

            if y.ndim > 1:
                y = y.mean(axis=1)

            return y, sr

        if isinstance(audio_input, str):
            import os
            if os.path.exists(audio_input):
                y, sr = librosa.load(audio_input, sr=None, mono=True)
                return y, sr

    except Exception as e:
        print(f"[voice_features] Load error: {e}")

    return None, 22050


def _zeros():
    return {
        "pitch_mean":  0.0,
        "pitch_std":   0.0,
        "pitch_min":   0.0,
        "pitch_max":   0.0,

        "energy_mean": 0.0,
        "energy_std":  0.0,

        "zcr_mean":    0.0,

        "mfcc_mean_1": 0.0,
        "mfcc_mean_2": 0.0,
        "mfcc_mean_3": 0.0,
    }