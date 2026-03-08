# 🏥 ASHA Sahayak — AI Health Triage Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0.3-red)
![MySQL](https://img.shields.io/badge/mysql-8.0-orange)
![License](https://img.shields.io/badge/license-MIT-purple)

**AI-powered health triage assistant for ASHA workers in rural India**
Built with Flask · MySQL · Groq AI · Multilingual Support

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Environment Setup](#-environment-setup)
- [Database Setup](#-database-setup)
- [Running the App](#-running-the-app)
- [Cloud Database (Azure)](#-cloud-database-azure)
- [Building .exe](#-building-exe-for-windows)
- [API Reference](#-api-reference)
- [Supported Languages](#-supported-languages)
- [AI Models](#-ai-models)
- [Triage Levels](#-triage-levels)
- [Troubleshooting](#-troubleshooting)

---

## 🌟 Overview

**ASHA Sahayak** is a multilingual AI health triage assistant designed specifically for **ASHA (Accredited Social Health Activist) workers** in rural India. It helps field workers assess patient symptoms, determine urgency levels, and provide actionable medical guidance — all in the worker's preferred language.

The app works as a **general AI assistant** by default and automatically switches to **health triage mode** when health-related symptoms are mentioned in any of the 5 supported languages.

---

## ✨ Features

### 🤖 AI Chat
- **General Assistant Mode** — answers any question in the selected language
- **Auto Health Triage Mode** — activates automatically when symptoms are mentioned
- Keyword detection in 5 languages (English, Hindi, Telugu, Kannada, Tamil)
- Conversational triage — gathers symptoms naturally, no forms
- Structured triage result: EMERGENCY / URGENT / MONITOR / HOME

### 👤 Patient Management
- Register new patients with ID, name, age, gender, village, phone
- Look up existing patients by Patient ID
- ⚠️ **12-hour revisit alert** — warns if patient visited within 12 hours
- 🚨 Emergency escalation alert for critical cases

### 📊 Dashboard
- View all registered patients and visit history
- Last triage level per patient
- Total visit count
- Color-coded severity badges

### 📋 IMCI Quick Reference
- WHO IMCI 2014 / MOHFW India IMNCI guidelines
- Emergency, Urgent, Monitor, and Home care categories
- Fully translated in all 5 languages

### 🌐 Multilingual UI
- One selector changes **both** the website UI and AI response language
- Full translations: English, हिंदी, తెలుగు, ಕನ್ನಡ, தமிழ்
- Auto-greeting in selected language on login

### 📋 Copy Button
- Every AI response has a copy button
- Works in all browsers including the Windows .exe version

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.8+, Flask 3.0.3 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Database | MySQL 8.0 (local or Azure cloud) |
| AI | Groq API (Llama 3.3 70B / Llama 3.1 8B / Mixtral / Gemma 2) |
| Fonts | Google Fonts — Nunito |
| Desktop | PyWebView (for .exe build) |

---

## 📁 Project Structure

```
asha_sahayak/
├── app.py                  ← Flask backend — all routes & AI logic
├── schema.sql              ← MySQL database schema + sample data
├── requirements.txt        ← Python dependencies
├── launcher.py             ← PyWebView launcher for .exe build
├── .env                    ← Environment variables (DO NOT commit)
├── .env.example            ← Template for .env
├── .vscode/
│   └── launch.json         ← VS Code debug configuration
└── templates/
    └── index.html          ← Complete single-file frontend UI
```

---

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** — [Download](https://python.org/downloads)
- **MySQL 8.0+** — [Download](https://dev.mysql.com/downloads/mysql/)
- **Groq API Key** (free) — [Get one](https://console.groq.com)
- **Git** (optional) — [Download](https://git-scm.com)

---

## 🚀 Installation

### 1. Clone or Download the Project

```bash
git clone https://github.com/yourname/asha-sahayak.git
cd asha-sahayak
```

Or just copy the project folder to `C:\Users\pawan\asha_sahayak\`

### 2. Create Virtual Environment

```powershell
# Windows
python -m venv venv
venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

```bash
# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt contents:**
```
flask==3.0.3
flask-cors==4.0.1
mysql-connector-python==8.4.0
groq==0.9.0
python-dotenv==1.0.1
```

---

## 🔐 Environment Setup

Create a `.env` file in the project root:

```env
# Groq AI API Key (get free at console.groq.com)
GROQ_API_KEY=gsk_your_key_here

# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=asha_sahayak

# Flask Secret Key
SECRET_KEY=asha-secret-2024
```

> ⚠️ **Never commit `.env` to Git.** Add it to `.gitignore`.

---

## 🗄️ Database Setup

### Local MySQL

```bash
# Connect to MySQL
mysql -u root -p

# Run schema
mysql -u root -p < schema.sql
```

This creates:

**`patients` table**
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| patient_id | VARCHAR(20) UNIQUE | e.g. ASHA001 |
| name | VARCHAR(100) | Full name |
| age | INT | Age in years |
| gender | ENUM | Male / Female / Other |
| village | VARCHAR(100) | Village name |
| phone | VARCHAR(15) | Phone number |
| created_at | DATETIME | Registration time |

**`visits` table**
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| patient_id | VARCHAR(20) | Foreign key → patients |
| visit_time | DATETIME | Visit timestamp |
| lang | VARCHAR(5) | Language code (en/hi/te/kn/ta) |
| model | VARCHAR(50) | AI model used |
| triage_level | ENUM | EMERGENCY/URGENT/MONITOR/HOME |
| chat_log | LONGTEXT | JSON array of messages |

### Clear All Data (if needed)

```sql
USE asha_sahayak;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE visits;
TRUNCATE TABLE patients;
SET FOREIGN_KEY_CHECKS = 1;
```

---

## ▶️ Running the App

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## ☁️ Cloud Database (Azure)

To share the database with team members / other ASHA workers:

### Step 1 — Create Azure MySQL Flexible Server

1. Go to [portal.azure.com](https://portal.azure.com)
2. Create Resource → **Azure Database for MySQL Flexible Server**
3. Settings:
   - Server name: `asha-sahayak-db`
   - Region: `Central India`
   - MySQL version: `8.0`
   - Tier: `Development` (cheapest)
   - Admin username: `ashaadmin`

### Step 2 — Allow Connections

- Networking → Firewall rules → Add `0.0.0.0` to `255.255.255.255`
- Enable **Allow public access**

### Step 3 — Update `.env`

```env
DB_HOST=asha-sahayak-db.mysql.database.azure.com
DB_PORT=3306
DB_USER=ashaadmin
DB_PASSWORD=YourAzurePassword123!
DB_NAME=asha_sahayak
```

### Step 4 — Enable SSL in `app.py`

```python
DB_CONFIG = {
    "host":         os.getenv("DB_HOST", "localhost"),
    "user":         os.getenv("DB_USER", "root"),
    "password":     os.getenv("DB_PASSWORD", ""),
    "database":     os.getenv("DB_NAME", "asha_sahayak"),
    "port":         int(os.getenv("DB_PORT", 3306)),
    "ssl_disabled": False,   # Required for Azure
}
```

### Step 5 — Push Schema to Azure

```bash
mysql -h asha-sahayak-db.mysql.database.azure.com -u ashaadmin -p asha_sahayak < schema.sql
```

> 💰 **Cost:** ~$0–$13/month on Development tier. New accounts get 750 free hours.

---

## 🖥️ Building .exe for Windows

### 1. Install PyInstaller & PyWebView

```bash
pip install pyinstaller pywebview
```

### 2. Fix Groq/httpx Version Conflict (if any)

```bash
pip uninstall groq httpx -y
pip install httpx==0.27.0 groq
```

### 3. Build the .exe

```bash
pyinstaller --noconfirm --onefile --windowed \
  --add-data "templates;templates" \
  --add-data ".env;." \
  --hidden-import flask \
  --hidden-import groq \
  --hidden-import mysql.connector \
  --name "ASHA_Sahayak" \
  launcher.py
```

Output: `dist/ASHA_Sahayak.exe`

### 4. Change App Name

In `launcher.py`:
```python
webview.create_window(
    "Your Custom Name",       # ← Change this
    "http://127.0.0.1:5000",
    width=1100,
    height=750,
)
```

And in the build command: `--name "YourCustomName"`

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve main UI |
| POST | `/api/patient/check` | Check if patient exists + 12hr alert |
| POST | `/api/patient/register` | Register new patient |
| POST | `/api/visit/start` | Start new visit session |
| POST | `/api/chat` | Send message, get AI response |
| POST | `/api/chat/exit-health` | Exit health triage mode |
| GET | `/api/dashboard` | Get all patients with visit stats |

### Example: Check Patient
```json
POST /api/patient/check
{ "patient_id": "ASHA001" }

Response:
{
  "exists": true,
  "patient": { "name": "Sunita Devi", "age": 32, ... },
  "alert_12hr": true,
  "hours_ago": 3.5,
  "last_triage": "URGENT"
}
```

### Example: Chat
```json
POST /api/chat
{ "message": "patient has high fever", "chat_lang": "hi" }

Response:
{
  "reply": "बुखार कितने दिनों से है?...",
  "mode": "health",
  "triage": null,
  "triage_done": false
}
```

---

## 🌐 Supported Languages

| Code | Language | UI | Chat | Health Keywords |
|------|----------|----|------|-----------------|
| `en` | English | ✅ | ✅ | ✅ |
| `hi` | हिंदी (Hindi) | ✅ | ✅ | ✅ |
| `te` | తెలుగు (Telugu) | ✅ | ✅ | ✅ |
| `kn` | ಕನ್ನಡ (Kannada) | ✅ | ✅ | ✅ |
| `ta` | தமிழ் (Tamil) | ✅ | ✅ | ✅ |

> Changing the language selector updates **both** the UI and the AI response language simultaneously.

---

## 🤖 AI Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `llama-3.3-70b-versatile` | Medium | ⭐⭐⭐⭐⭐ | Best accuracy, default |
| `llama-3.1-8b-instant` | ⚡ Fast | ⭐⭐⭐ | Quick responses |
| `mixtral-8x7b-32768` | Medium | ⭐⭐⭐⭐ | Long conversations |
| `gemma2-9b-it` | Fast | ⭐⭐⭐ | Lightweight option |

All models are **free** via [Groq API](https://console.groq.com).

---

## 🚦 Triage Levels

| Level | Color | Action |
|-------|-------|--------|
| 🚨 EMERGENCY | Red | Call 108 immediately |
| ⚠️ URGENT | Orange | Visit PHC within 24 hours |
| 👁️ MONITOR | Blue | Home care, monitor 2–3 days |
| 🏠 HOME | Green | Rest, ORS, Paracetamol |

### Red Flags (auto-EMERGENCY)
- Fever + stiff neck → **Meningitis**
- Chest pain + sweating → **Cardiac**
- Infant breathing difficulty → **Pneumonia**
- Unconscious/not responding → **Critical**
- Convulsions/seizures → **Seizure**
- Blood in vomit or stool → **Bleeding**

---

## 🔧 Troubleshooting

### MySQL Connection Error
```
Error: Can't connect to MySQL server
```
**Fix:** Make sure MySQL is running:
```powershell
# Windows
net start MySQL80

# Check password in .env matches MySQL root password
```

### Groq API Error — Invalid Key
```
🔑 Invalid API key
```
**Fix:** Get a free key at [console.groq.com](https://console.groq.com) and update `.env`

### Rate Limit Hit
```
⚠️ Rate limit hit. Wait 1 minute or switch model.
```
**Fix:** Switch to `Llama 8B ⚡` model (higher rate limits) or wait 60 seconds

### .exe Crash — proxies error
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```
**Fix:**
```bash
pip uninstall groq httpx -y
pip install httpx==0.27.0 groq
```
Then rebuild the .exe.

### PowerShell Execution Policy Error
```
cannot be loaded because running scripts is disabled
```
**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 👨‍💻 Developer

**Yarra Pawan**
Built for ASHA health workers in rural India 🇮🇳

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*ASHA Sahayak — Empowering healthcare at the grassroots level* 🌿
