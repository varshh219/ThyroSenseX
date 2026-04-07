import json
import os
import uuid
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "patients.json")


def _load():
    """Load database from JSON file."""
    if not os.path.exists(DB_PATH):
        _save({"patients": []})
    with open(DB_PATH, "r") as f:
        return json.load(f)


def _save(data):
    """Save database to JSON file."""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)


def generate_patient_id():
    """Generate unique patient ID like TSX-2026-0001."""
    db = _load()
    count = len(db["patients"]) + 1
    year  = datetime.now().year
    return f"TSX-{year}-{count:04d}"


def register_patient(name, age, gender, phone, address):
    """
    Register a new patient.
    Returns the new patient dict.
    """
    db = _load()

    patient = {
        "id":        generate_patient_id(),
        "name":      name.strip(),
        "age":       int(age),
        "gender":    gender,
        "phone":     phone.strip(),
        "address":   address.strip(),
        "created":   datetime.now().strftime("%d %b %Y %H:%M"),
        "scans":     [],
    }

    db["patients"].append(patient)
    _save(db)
    print(f"✓ Patient registered: {patient['id']} — {patient['name']}")
    return patient


def get_all_patients():
    """Return list of all patients."""
    db = _load()
    return db["patients"]


def search_patients(query):
    """
    Search patients by name or ID.
    Returns list of matching patients.
    """
    db     = _load()
    query  = query.lower().strip()
    return [
        p for p in db["patients"]
        if query in p["name"].lower()
        or query in p["id"].lower()
    ]


def get_patient_by_id(patient_id):
    """Get a single patient by ID."""
    db = _load()
    for p in db["patients"]:
        if p["id"] == patient_id:
            return p
    return None


def save_scan_result(patient_id, result):
    """
    Save a scan result to patient's history.
    result: dict with prediction, confidence, features etc.
    """
    db = _load()
    for p in db["patients"]:
        if p["id"] == patient_id:
            scan = {
                "date":       datetime.now().strftime("%d %b %Y %H:%M"),
                "prediction": result.get("prediction"),
                "confidence": result.get("confidence"),
                "probabilities": result.get("probabilities", {}),
            }
            p["scans"].append(scan)
            _save(db)
            print(f"✓ Scan saved for patient {patient_id}")
            return
    print(f"✗ Patient {patient_id} not found")