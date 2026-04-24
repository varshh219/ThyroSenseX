import psycopg2
import psycopg2.extras
import bcrypt
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ── CONNECTION ───────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "thyrosensex_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )


# ── DOCTOR AUTH ──────────────────────────────────────────────
def verify_doctor(username, password):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM doctors WHERE username=%s",
                    (username,)
                )
                doctor = cur.fetchone()

        if doctor and bcrypt.checkpw(
            password.encode(), doctor['password_hash'].encode()
        ):
            return dict(doctor)

    except Exception as e:
        print("DB Error (verify_doctor):", e)

    return None


def register_doctor(username, password, full_name, email):
    try:
        password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO doctors 
                    (username, password_hash, full_name, email)
                    VALUES (%s,%s,%s,%s) RETURNING id""",
                    (username, password_hash, full_name, email)
                )
                doctor_id = cur.fetchone()[0]

        return doctor_id

    except Exception as e:
        print("DB Error (register_doctor):", e)
        return None


# ── PATIENT ID GENERATION ────────────────────────────────────
def generate_patient_id():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM patients")
                count = cur.fetchone()[0] + 1

        return f"TSX-{datetime.now().year}-{count:04d}"

    except Exception as e:
        print("DB Error (generate_patient_id):", e)
        return f"TSX-{datetime.now().year}-0000"


# ── PATIENT OPERATIONS ───────────────────────────────────────
def register_patient(name, age, gender, phone, email, address, doctor_id):
    try:
        patient_id = generate_patient_id()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO patients
                    (patient_id, name, age, gender, phone, email, address, created_by)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (patient_id, name, age, gender, phone, email, address, doctor_id)
                )

        return {
            'id': patient_id,
            'name': name,
            'age': age,
            'gender': gender,
            'phone': phone,
            'email': email
        }

    except Exception as e:
        print("DB Error (register_patient):", e)
        return None


def search_patients(query):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """SELECT * FROM patients
                    WHERE LOWER(name) LIKE %s OR patient_id LIKE %s
                    ORDER BY created_at DESC""",
                    (f'%{query.lower()}%', f'%{query}%')
                )
                return [dict(r) for r in cur.fetchall()]

    except Exception as e:
        print("DB Error (search_patients):", e)
        return []


def get_all_patients():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM patients ORDER BY created_at DESC")
                return [dict(r) for r in cur.fetchall()]

    except Exception as e:
        print("DB Error (get_all_patients):", e)
        return []


# ── SCAN STORAGE ─────────────────────────────────────────────
def save_scan_result(patient_id, doctor_id, result):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO scans
                    (patient_id, doctor_id, prediction, confidence,
                     probabilities, features)
                    VALUES (%s,%s,%s,%s,%s,%s)""",
                    (
                        patient_id,
                        doctor_id,
                        result.get('prediction'),
                        result.get('confidence'),
                        json.dumps(result.get('probabilities', {})),
                        json.dumps(result.get('features', {}))
                    )
                )

    except Exception as e:
        print("DB Error (save_scan_result):", e)


def get_patient_scans(patient_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM scans WHERE patient_id=%s ORDER BY scan_date DESC",
                    (patient_id,)
                )
                return [dict(r) for r in cur.fetchall()]

    except Exception as e:
        print("DB Error (get_patient_scans):", e)
        return []