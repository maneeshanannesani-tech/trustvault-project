# TrustVault — Secure Multi-Tenant Document Vault & Access Control

TrustVault is a lightweight, secure document vault and access control system built using FastAPI, SQLite, and Jinja2 templates. It provides email-based registration, tenant-isolated file storage, granular document sharing, and an immutable audit trail.

---

## 🚀 Live Demo & Links
- **Live Application:** [https://trustvault-project-wqg8.onrender.com](https://trustvault-project-wqg8.onrender.com)
- **GitHub Repository:** [https://github.com/maneeshanannesani-tech/trustvault-project](https://github.com/maneeshanannesani-tech/trustvault-project)

---

## ✨ Features
- **User Authentication:** Simple email-based onboarding and session management.
- **Document Management:** Upload, preview, and download documents within isolated user accounts.
- **Access Control & Sharing:** Share documents with other users securely via their registered email address.
- **Tamper-Evident Audit Logging:** Real-time event tracking for logins, document uploads, and sharing activities.
- **Cross-Tenant Protection:** Strict backend query filters to prevent unauthorized file access.

---

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, Tailwind CSS, Jinja2 Templates
- **Database:** SQLite3
- **Hosting & Deployment:** Render, GitHub

---

## 💻 Local Setup & Installation

Clone the repository and run the project locally using these commands:

```bash
# 1. Clone the repository
git clone [https://github.com/maneeshanannesani-tech/trustvault-project.git](https://github.com/maneeshanannesani-tech/trustvault-project.git)

# 2. Navigate to project folder
cd trustvault-project

# 3. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize SQLite Database
python database.py

# 6. Start the server
uvicorn app:app --host 0.0.0.0 --port 8000
