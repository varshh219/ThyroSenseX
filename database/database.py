import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="thyrosensex_db",
    user="postgres",
    password="varsh123"   # ← change this
)

cursor = conn.cursor()

print("[DB] Connected to PostgreSQL")


# ─────────────────────────────────────────
# REGISTER PATIENT
# ─────────────────────────────────────────

def register_patient(name, age, gender, phone, email, address, doctor_id, weight):
    cursor.execute("""
        INSERT INTO patients (name, age, gender, weight, phone, email, address, doctor_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (name, age, gender, weight, phone, email, address, doctor_id))

    pid = cursor.fetchone()[0]
    conn.commit()

    return {
        "id": pid,
        "name": name,
        "age": age,
        "gender": gender,
        "weight": weight,
        "phone": phone
    }


# ─────────────────────────────────────────
# GET ALL PATIENTS
# ─────────────────────────────────────────

def get_all_patients():
    cursor.execute("SELECT id, name, age, gender, weight, phone FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()

    patients = []
    for r in rows:
        patients.append({
            "id": r[0],
            "name": r[1],
            "age": r[2],
            "gender": r[3],
            "weight": r[4],
            "phone": r[5]
        })

    return patients


# ─────────────────────────────────────────
# SAVE SCAN
# ─────────────────────────────────────────

def save_scan(patient_id, prediction, confidence):
    cursor.execute("""
        INSERT INTO scans (patient_id, prediction, confidence)
        VALUES (%s,%s,%s)
    """, (patient_id, prediction, confidence))

    conn.commit()


# ─────────────────────────────────────────
# GET LAST SCAN
# ─────────────────────────────────────────

def get_last_scan(patient_id):
    cursor.execute("""
        SELECT prediction, confidence, created_at
        FROM scans
        WHERE patient_id=%s
        ORDER BY created_at DESC
        LIMIT 1
    """, (patient_id,))

    row = cursor.fetchone()

    if not row:
        return None

    return {
        "prediction": row[0],
        "confidence": row[1],
        "date": row[2].strftime("%d %b %Y")
    }

    # ─────────────────────────────────────────
# VERIFY DOCTOR LOGIN
# ─────────────────────────────────────────
def verify_doctor(username, password):
    cursor.execute("""
        SELECT id, full_name FROM doctors
        WHERE full_name=%s AND password=%s
    """, (username, password))

    row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "full_name": row[1]
    }