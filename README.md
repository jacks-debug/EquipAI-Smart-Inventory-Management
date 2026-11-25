# EquipAI - AI-Powered College Equipment Inventory

**Run (one click):** double-click `run.bat` (Windows) or `bash run.sh` (Mac/Linux) -> open http://127.0.0.1:5000
Login: `admin@college.edu` / `admin123` (also hod@, lab@, faculty@ college.edu)

## Topic-wise code map
| Topic | Backend | Frontend |
|---|---|---|
| 1. Core, DB, demo data | `app/core.py`, `app/seed.py`, `app/__init__.py` | `static/js/core.js` |
| 2. Authentication, roles, profile | `app/routes/auth.py` | `js/auth.js`, `js/pages/admin.js` |
| 3. Dashboard | `app/routes/dashboard.py`, `services/inventory.py` | `js/pages/dashboard.js` |
| 4. Equipment management + export | `app/routes/equipment.py` | `js/pages/equipment.js` |
| 5. Issue & return | `app/routes/loans.py` | `js/pages/requests.js` |
| 6. AI: demand, maintenance, alerts, recommendations | `services/ai_engine.py`, `routes/ai.py` | `js/pages/ai.js`, `js/pages/alerts.js` |
| 7. EquipAI chatbot (reads live DB) | `routes/ai.py` (`chat`) | `js/pages/chat.js` |
| 8. UI shell and theme | `templates/index.html` | `js/shell.js`, `static/css/*.css` |

Test: `python tests/test_smoke.py`. Set `SECRET_KEY` for production.
Password reset token prints in the server console (connect SMTP for real email).
