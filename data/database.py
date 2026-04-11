import psycopg2
import psycopg2.extras
import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Connect to PostgreSQL ────────────────────────────────────
def get_connection():
    return psycopg2.connect(
        host     = os.getenv("DB_HOST", "localhost"),
        port     = os.getenv("DB_PORT", 5432),
        dbname   = os.getenv("DB_NAME", "thyrosensex_db"),
        user     = os.getenv("DB_USER", "postgres"),
        password = os.getenv("DB_PASSWORD", "")
    )

# ── Doctor Authentication ────────────────────────────────────
def verify_doctor(username, password):
    """Returns doctor dict if valid, None if invalid."""
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM doctors WHERE username = %s", (username,)
    )
    doctor = cur.fetchone()
    conn.close()
    if doctor and bcrypt.checkpw(
        password.encode(), doctor['password_hash'].encode()
    ):
        return dict(doctor)
    return None

def register_doctor(username, password, full_name, email):
    """Register a new doctor with hashed password."""
    password_hash = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        """INSERT INTO doctors (username, password_hash, full_name, email)
           VALUES (%s, %s, %s, %s) RETURNING id""",
        (username, password_hash, full_name, email)
    )
    doctor_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return doctor_id

# ── Patient Operations ───────────────────────────────────────
def generate_patient_id():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM patients')
    count = cur.fetchone()[0] + 1
    conn.close()
    return f'TSX-{datetime.now().year}-{count:04d}'

def register_patient(name, age, gender, phone, email, address, doctor_id):
    patient_id = generate_patient_id()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        """INSERT INTO patients
           (patient_id, name, age, gender, phone, email, address, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (patient_id, name, age, gender, phone, email, address, doctor_id)
    )
    conn.commit()
    conn.close()
    return {'id': patient_id, 'name': name, 'age': age,
            'gender': gender, 'phone': phone, 'email': email}

def search_patients(query):
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT * FROM patients
           WHERE LOWER(name) LIKE %s OR patient_id LIKE %s
           ORDER BY created_at DESC""",
        (f'%{query.lower()}%', f'%{query}%')
    )
    results = [dict(r) for r in cur.fetchall()]
    conn.close()
    return results

def get_all_patients():
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients ORDER BY created_at DESC')
    results = [dict(r) for r in cur.fetchall()]
    conn.close()
    return results

def save_scan_result(patient_id, doctor_id, result):
    import json
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        """INSERT INTO scans
           (patient_id, doctor_id, prediction, confidence,
            probabilities, features)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (patient_id, doctor_id,
         result.get('prediction'),
         result.get('confidence'),
         json.dumps(result.get('probabilities', {})),
         json.dumps(result.get('features', {})))
    )
    conn.commit()
    conn.close()

def get_patient_scans(patient_id):
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM scans WHERE patient_id=%s ORDER BY scan_date DESC",
        (patient_id,)
    )
    results = [dict(r) for r in cur.fetchall()]
    conn.close()
    return results