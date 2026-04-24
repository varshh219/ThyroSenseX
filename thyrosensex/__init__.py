"""
thyroxensex/__init__.py
───────────────────────
Runs on Raspberry Pi — imported by pi_server.py.

Exports the three feature extractors used in /scan_face pipeline.
Each extractor returns a flat dict of feature key→value pairs
that get merged into the final response JSON.
"""

from .face_features import extract_face_features
from .thermal_features import extract_thermal_features
from .voice_features import extract_voice_features

__all__ = [
    "extract_face_features",
    "extract_thermal_features",
    "extract_voice_features"
]