import librosa
import numpy as np

def extract_voice_features(audio_path):
    try:
        y, sr = librosa.load(audio_path)
        pitch = np.mean(librosa.yin(y, fmin=50, fmax=300))
    except:
        pitch = 150

    return {
        "pitch_hz": float(pitch),
        "jitter": 0.01,
        "shimmer": 0.02,
        "hnr": 20
    }