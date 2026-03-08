"""
ASHA Sahayak — Flask + MySQL Backend
Run: python app.py
"""

from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
from groq import Groq
import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "asha-secret-2024")
CORS(app)

# ──────────────────────────────────────────────
# MySQL Connection Pool
# ──────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "asha_sahayak"),
    "port":     int(os.getenv("DB_PORT", 3306)),
}

pool = pooling.MySQLConnectionPool(pool_name="asha_pool", pool_size=5, **DB_CONFIG)

def get_db():
    return pool.get_connection()


# ──────────────────────────────────────────────
# Groq Client
# ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_key_here")
groq_client  = Groq(api_key=GROQ_API_KEY)

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada",
    "ta": "Tamil"
}

HEALTH_KEYWORDS = [
    "fever","sick","pain","vomit","cough","breath","hospital","doctor","medicine",
    "headache","diarrhea","rash","swelling","unconscious","seizure","bleeding",
    "chest","throat","infection","symptoms","ill","unwell","hurt","ache","nausea",
    "dizziness","faint","pregnancy","infant","baby","child","temperature",
    "बुखार","दर्द","बीमार","उल्टी","खांसी","सांस","अस्पताल","दवा","सिरदर्द","दस्त","बच्चा",
    "జ్వరం","నొప్పి","వాంతి","దగ్గు","శ్వాస","ఆసుపత్రి",
    "ಜ್ವರ","ನೋವು","ವಾಂತಿ","ಕೆಮ್ಮು","ಶ್ವಾಸ","ಆಸ್ಪತ್ರೆ",
    "காய்ச்சல்","வலி","வாந்தி","இருமல்","மருத்துவமனை",
]

# ── FIXED: Language rule added to GENERAL_SYSTEM ──
GENERAL_SYSTEM = """You are ASHA Sahayak — a friendly, intelligent, warm AI assistant.
You help with any topic: general knowledge, advice, calculations, creative writing, translations, coding.

CRITICAL LANGUAGE RULE: You MUST always respond in {lang_name} only.
No matter what language the user types in, always reply in {lang_name}.
Do not switch languages. Do not respond in English unless {lang_name} is English.

Keep responses concise and conversational. Sound human and warm. Never be robotic."""

HEALTH_SYSTEM = """You are ASHA Sahayak in health triage mode — a warm medical triage assistant for ASHA workers in rural India.

CRITICAL LANGUAGE RULE: You MUST always respond in {lang_name} only.
No matter what language the user types in, always reply in {lang_name}.

YOUR STYLE:
- Warm, caring, conversational like a knowledgeable friend
- Ask ONE question at a time naturally
- Acknowledge what user said before asking next question
- Never use numbered lists or forms

GATHER through natural conversation:
1. Patient age and gender
2. Main complaint
3. Fever — present? how many days? how high?
4. Breathing difficulty?
5. Conscious and responding normally?
6. Able to eat/drink? Any vomiting?
7. How many days has this been going on?
8. Any other symptoms — diarrhea, rash, pain, swelling?

RED FLAGS — if mentioned, immediately say EMERGENCY and advise to call 108:
- Fever + stiff neck → Meningitis
- Chest pain + sweating → Cardiac
- Infant breathing difficulty → Pneumonia
- Unconscious → Critical
- Convulsions/seizures → Seizure
- Blood in vomit → Bleeding

After 6-8 exchanges when you have enough info, output EXACTLY this block:

---TRIAGE_RESULT---
LEVEL: [EMERGENCY/URGENT/MONITOR/HOME]
REASONING: [1-2 sentences in English]
ADVICE: [detailed advice in {lang_name}]
---END_TRIAGE---

Then add nearby facility recommendations in {lang_name}.
IMPORTANT: Never output the triage block early. Always sound human."""


# ──────────────────────────────────────────────
# DB Helpers
# ──────────────────────────────────────────────
def db_get_patient(patient_id: str):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

def db_create_patient(patient_id, name, age, gender, village, phone):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO patients (patient_id, name, age, gender, village, phone, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (patient_id, name, age, gender, village, phone))
    conn.commit()
    cur.close(); conn.close()

def db_create_visit(patient_id, lang, model):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO visits (patient_id, visit_time, lang, model, triage_level, chat_log)
        VALUES (%s, NOW(), %s, %s, NULL, '[]')
    """, (patient_id, lang, model))
    visit_id = cur.lastrowid
    conn.commit()
    cur.close(); conn.close()
    return visit_id

def db_update_visit(visit_id, triage_level, chat_log):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE visits SET triage_level = %s, chat_log = %s WHERE id = %s
    """, (triage_level, chat_log, visit_id))
    conn.commit()
    cur.close(); conn.close()

def db_last_visit(patient_id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM visits WHERE patient_id = %s
        ORDER BY visit_time DESC LIMIT 1
    """, (patient_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

def db_check_12hr_alert(patient_id):
    last = db_last_visit(patient_id)
    if not last:
        return False, None
    diff = datetime.datetime.now() - last["visit_time"]
    if diff.total_seconds() < 12 * 3600:
        return True, last
    return False, None

def db_get_all_patients():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, COUNT(v.id) as visit_count, MAX(v.visit_time) as last_visit,
               MAX(v.triage_level) as last_triage
        FROM patients p
        LEFT JOIN visits v ON p.patient_id = v.patient_id
        GROUP BY p.patient_id
        ORDER BY last_visit DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


# ──────────────────────────────────────────────
# LLM Helpers
# ──────────────────────────────────────────────
def is_health_query(text):
    lower = text.lower()
    return any(kw in lower for kw in HEALTH_KEYWORDS)

def parse_triage(text):
    if "---TRIAGE_RESULT---" not in text:
        return None
    try:
        s = text.index("---TRIAGE_RESULT---") + len("---TRIAGE_RESULT---")
        e = text.index("---END_TRIAGE---")
        result = {}
        for line in text[s:e].strip().splitlines():
            if line.startswith("LEVEL:"):       result["level"]     = line.replace("LEVEL:", "").strip()
            elif line.startswith("REASONING:"): result["reasoning"] = line.replace("REASONING:", "").strip()
            elif line.startswith("ADVICE:"):    result["advice"]    = line.replace("ADVICE:", "").strip()
        return result if "level" in result else None
    except:
        return None

def clean_text(text):
    if "---TRIAGE_RESULT---" in text and "---END_TRIAGE---" in text:
        s = text.index("---TRIAGE_RESULT---")
        e = text.index("---END_TRIAGE---") + len("---END_TRIAGE---")
        text = text[:s] + text[e:]
    return text.strip()


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/patient/check", methods=["POST"])
def patient_check():
    data       = request.json
    patient_id = data.get("patient_id", "").strip().upper()
    if not patient_id:
        return jsonify({"error": "Patient ID required"}), 400
    patient = db_get_patient(patient_id)
    if patient:
        alert, last_visit = db_check_12hr_alert(patient_id)
        hours_ago = None
        last_visit_str = None
        if last_visit:
            last_visit_str = last_visit["visit_time"].strftime("%H:%M %d/%m/%Y")
            diff = datetime.datetime.now() - last_visit["visit_time"]
            hours_ago = round(diff.total_seconds() / 3600, 1)
        return jsonify({
            "exists":      True,
            "patient":     {k: str(v) if isinstance(v, (datetime.date, datetime.datetime)) else v
                            for k, v in patient.items()},
            "alert_12hr":  alert,
            "last_visit":  last_visit_str,
            "hours_ago":   hours_ago,
            "last_triage": last_visit["triage_level"] if last_visit else None,
        })
    return jsonify({"exists": False})

@app.route("/api/patient/register", methods=["POST"])
def patient_register():
    data       = request.json
    patient_id = data.get("patient_id", "").strip().upper()
    name       = data.get("name", "").strip()
    age        = int(data.get("age", 0))
    gender     = data.get("gender", "")
    village    = data.get("village", "").strip()
    phone      = data.get("phone", "").strip()
    if not all([patient_id, name, age, gender]):
        return jsonify({"error": "Name, age, gender required"}), 400
    if db_get_patient(patient_id):
        return jsonify({"error": "Patient ID already exists"}), 409
    db_create_patient(patient_id, name, age, gender, village, phone)
    return jsonify({"success": True, "patient_id": patient_id})

@app.route("/api/visit/start", methods=["POST"])
def visit_start():
    data       = request.json
    patient_id = data.get("patient_id", "").strip().upper()
    lang       = data.get("lang", "en")
    model      = data.get("model", "llama-3.3-70b-versatile")
    patient = db_get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    visit_id = db_create_visit(patient_id, lang, model)
    session["visit_id"]        = visit_id
    session["patient_id"]      = patient_id
    session["lang"]            = lang
    session["model"]           = model
    session["mode"]            = "general"
    session["health_history"]  = []
    session["general_history"] = []
    return jsonify({"success": True, "visit_id": visit_id})

@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.json
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    visit_id = session.get("visit_id")
    # ── FIXED: always use lang from request (UI language = chat language) ──
    lang  = data.get("chat_lang") or session.get("lang", "en")
    session["lang"] = lang
    model = session.get("model", "llama-3.3-70b-versatile")
    lang_name = LANG_NAMES.get(lang, "English")

    # Auto-detect health mode
    if is_health_query(message) or session.get("mode") == "health":
        session["mode"] = "health"

    mode = session.get("mode", "general")

    try:
        if mode == "health":
            # ── FIXED: replace lang_name in health system ──
            system = HEALTH_SYSTEM.replace("{lang_name}", lang_name)
            h = session.get("health_history", [])
            h.append({"role": "user", "content": message})

            resp = groq_client.chat.completions.create(
                model=model, max_tokens=800, timeout=25,
                messages=[{"role": "system", "content": system}] + h,
            )
            raw = resp.choices[0].message.content.strip()
            h.append({"role": "assistant", "content": raw})
            session["health_history"] = h

            triage  = parse_triage(raw)
            display = clean_text(raw)

            if triage and visit_id:
                db_update_visit(visit_id, triage["level"], json.dumps(h))

            return jsonify({
                "reply":       display,
                "mode":        "health",
                "triage":      triage,
                "triage_done": triage is not None,
            })

        else:
            # ── FIXED: replace lang_name in general system ──
            system = GENERAL_SYSTEM.replace("{lang_name}", lang_name)
            h = session.get("general_history", [])
            h.append({"role": "user", "content": message})
            msgs = h[-20:]

            resp = groq_client.chat.completions.create(
                model=model, max_tokens=800, timeout=25,
                messages=[{"role": "system", "content": system}] + msgs,
            )
            raw = resp.choices[0].message.content.strip()
            h.append({"role": "assistant", "content": raw})
            session["general_history"] = h

            return jsonify({"reply": raw, "mode": "general", "triage": None})

    except Exception as e:
        err = str(e)
        if "401" in err or "invalid" in err.lower():
            msg = "🔑 Invalid API key. Check GROQ_API_KEY in .env"
        elif "429" in err or "rate" in err.lower():
            msg = "⚠️ Rate limit hit. Wait 1 minute or switch model."
        elif "timeout" in err.lower():
            msg = "⏱️ Request timed out. Try again."
        else:
            msg = f"❌ Error: {err}"
        return jsonify({"reply": msg, "mode": mode, "triage": None})

@app.route("/api/chat/exit-health", methods=["POST"])
def exit_health():
    session["mode"] = "general"
    session["health_history"] = []
    return jsonify({"success": True})

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    patients = db_get_all_patients()
    result = []
    for p in patients:
        row = {}
        for k, v in p.items():
            row[k] = v.strftime("%H:%M %d/%m/%Y") if isinstance(v, (datetime.date, datetime.datetime)) else v
        result.append(row)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)