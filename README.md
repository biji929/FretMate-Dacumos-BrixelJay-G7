# FretMate: Guitar Practice & Skill-Analytics Platform

**Course:** Information Management 2 (IM2)  
**Institution:** Cebu Institute of Technology - University (CIT-U)  
**Developer / Student:** Brixel Jay Dacumos  
**Section:** G7  
**Academic Year:** 2026–2027  
**Official Repository:** [https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7](https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7)  
**Deliverables Document:** [`docs/FretMate-Dacumos-BrixelJay-G7-PD2.pdf`](docs/FretMate-Dacumos-BrixelJay-G7-PD2.pdf)  

---

## 📌 Project Overview
**FretMate** is an integrated web-based guitar practice companion and skill-analytics platform designed for self-directed guitarists and music educators. It centralizes essential practice utilities—interactive chord libraries, 15-fret interactive SVG fretboard exploration, real-time chord transposer, song tablature with backing track video synchronization, precision Web Audio chromatic tuners, and lookahead metronomes—while offering deep practice analytics (daily streaks, goal completion percentages, and category time distribution).

---

## 🎯 Project Development 2 (PD2) — Core Feature (Vertical Slice)

### What is the Core Feature?
The designated Core Feature of FretMate is **Guitar Practice Session Logging & Skill Management (Practice Logger)**. This is the central operational engine of the system upon which all guitarist analytics (daily streaks, weekly goals, Chart.js trend charts) and instructor oversight depend.

### Full Working Vertical Slice
The Core Feature operates end-to-end through every layer of the system:
1. **Database Layer:** PostgreSQL / Supabase storing `PracticeSession` (`duration_minutes`, `focus_area`, `notes`, `date`, `user_id`). Models use foreign keys, indexes, and user-level data isolation.
2. **Backend Layer:** Django views (`logger`, `get_practice_session`, `update_practice_session`, `delete_practice_session`, `export_practice_csv`), Django ModelForms (`PracticeSessionForm`), strict `@login_required` decorators, and RESTful AJAX JSON responses.
3. **Frontend Layer:** Responsive Django templates (`templates/logger.html`, `templates/dashboard_guitarist.html`, `templates/dashboard_instructor.html`, `templates/instructor_student_detail.html`) styled in the modern Electric Crimson & Obsidian dark palette with asynchronous modal dialogs, in-place DOM updates, and instant CSV export.

### CRUD Operations
- **CREATE (`POST /logger/`):** Guitarist logs practice duration, focus area (`Chords`, `Songs`, `Scales`, `Rhythm`), and notes. Submitted asynchronously via AJAX and dynamically prepended to the feed.
- **READ (`GET /logger/`, `GET /logger/<id>/`, `GET /export/practice-csv/`):** History feed displays past sessions; single session endpoint populates the Edit modal; CSV export streams user's full practice history.
- **UPDATE (`POST /logger/<id>/update/`):** Edit button opens a sleek crimson modal pre-filled with data. Updates validate and persist to PostgreSQL and reflect instantly in the UI.
- **DELETE (`POST /logger/<id>/delete/`):** Delete button prompts a confirmation modal. On confirmation, the record is removed from PostgreSQL and the DOM card animates out.

---

## 🛡️ Standard Features (PD1 Baseline — 100% Maintained)
1. **Account Registration (`/register/`):** Streamlined sign-up with RFC-compliant unique email validation, unique username, strong password checks, and role assignment (`Guitarist` or `Instructor`). Guest users clicking **Register Free** automatically keep their logged practice sessions and chord mastery when upgrading.
2. **Role-First Sign In & Logout (`/login/`, `/logout/`):** Two-step sign-in asking **Student** or **Instructor** first with backend role-match validation, PBKDF2 authentication, CSRF-safe logout, and one-click guest access.
3. **Role-Based User Dashboards (`/dashboard/`):** Automatic dispatch via `@role_required`. Guitarist views personal 7-day practice stats; Instructor views enrolled student roster and drill-down logs (`/instructor/student/<id>/`).
4. **User Profile Management (`/profile/`):** Viewing and editing musician name, contact number, biography, skill tier, and weekly goal minutes with strict user data isolation.

---

## 🔑 Test Accounts & Evaluation Credentials

Run `python manage.py seed_data` to ensure these test accounts and sample practice records exist:

| Role | Username | Email | Password | Purpose & Privileges |
| :--- | :--- | :--- | :--- | :--- |
| **Guitarist (Student)** | `guitarist_user` | `guitarist@fretmate.test` | `Testpass123!` | Full CRUD practice session logging, personal analytics, fretboard explorer, chord transposer. |
| **Instructor (Teacher)** | `instructor_user` | `instructor@fretmate.test` | `Testpass123!` | Instructor dashboard, student roster, student practice log drill-down (`/instructor/student/<id>/`). |
| **Guest Explorer** | Instant Guest Access | — | None (One-Click) | Temporary session created from landing page; persistent top banner with seamless account upgrade. |

---

## 🛠️ Technology Stack
- **Backend & Web Framework:** Python 3.12+ / Django 6.x
- **Frontend & Templates:** Django Server-Side Templates, Tailwind CSS (Electric Crimson & Obsidian Dark Theme)
- **Data Visualizations:** Chart.js (Practice trend line charts, focus area distribution doughnuts)
- **Audio Processing:** Client-Side Web Audio API (Autocorrelation Tuner, Lookahead Metronome, Pluck Synthesis)
- **Database:** PostgreSQL / Supabase (`psycopg3`, `dj-database-url`) with local SQLite fallback for development
- **Security & Static Files:** Django Built-in Authentication, CSRF Protection, WhiteNoise

---

## 💻 Local Setup & Execution Guide

### Prerequisites
- Python 3.12+ installed
- Git installed

### 1. Clone & Set Up Virtual Environment
```powershell
# Clone the repository
git clone https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7.git
cd FretMate-Dacumos-BrixelJay-G7

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the `.env.example` file to `.env`:
```powershell
Copy-Item .env.example .env
```
*(Leave `DATABASE_URL` empty to run on the local SQLite development database, or provide your Supabase PostgreSQL connection string for production).*

### 4. Run Migrations & Seed Data
```powershell
python manage.py migrate
python manage.py seed_data
```

### 5. Run Automated Tests
```powershell
python manage.py test
```
*Expected: 22 of 22 tests pass successfully.*

### 6. Start Development Server
```powershell
python manage.py runserver
```
Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🌿 GitHub Branching Strategy

In strict accordance with academic specifications:
- `main`: Stable release branch. Direct commits prohibited.
- `develop`: Integration branch created from `main`.
- `feature/<name>`: Dedicated feature branches branched from `develop` and merged via Pull Requests. Merged branches are preserved.

| Branch Name | Base Branch | Target Branch | Pull Request / Objective |
| :--- | :--- | :--- | :--- |
| `feature/practice-session-crud` | `develop` | `develop` | Practice Session Update and Delete (Full CRUD), modal UI, AJAX responses, and test suite. |
| `feature/pd2-docs-and-report` | `develop` | `develop` | Initial PD2 completion report PDF in `docs/` and README documentation. |
| `feature/guest-account-upgrade` | `develop` | `develop` | Allow guest accounts to register and migrate guest practice sessions & chord mastery. |
| `feature/simplify-registration-form` | `develop` | `develop` | Streamlined registration form and username fallbacks across views/templates. |
| `feature/fix-fretboard-hover` | `develop` | `develop` | Fix SVG fretboard note hover stability with crimson glow & pluck feedback. |
| `feature/role-first-signin` | `develop` | `develop` | Two-step Student / Instructor Sign In with backend role-match verification. |
| `feature/fretmate-brand-logo` | `develop` | `develop` | Minimalist guitar-pick FretMate SVG logo & favicon across all layouts. |
| `feature/pd2-test-accounts-and-docs` | `develop` | `develop` | **PR #1:** Seed official evaluation test accounts (`guitarist_user` / `instructor_user`) and update README. |
| `feature/pd2-completion-report-final` | `develop` | `develop` | **PR #2:** Official PD2 completion report PDF (matching course template with screenshots & PR links). |
| `develop` | `main` | `main` | **PR #3:** Final Project Development 2 increment release into production `main`. |

---

## 📂 Project Structure
```text
FretMate/
│
├── dashboard/                     # Main application
│   ├── models.py                  # UserProfile, Chord, Tab, PracticeSession, UserChordProgress
│   ├── views.py                   # Role dashboards, auth flows, CRUD endpoints, CSV export
│   ├── forms.py                   # RegistrationForm, UserProfileUpdateForm, PracticeSessionForm
│   ├── urls.py                    # Application routing
│   ├── admin.py                   # Model registration with filters
│   └── tests.py                   # 22 automated unit tests (100% pass)
│
├── docs/                          # Course deliverables
│   ├── FretMate-Dacumos-BrixelJay-G7-PD2.pdf # Official PD2 completion report PDF
│   └── PD2_Report.md              # Markdown version of PD2 report
│
├── fretmate_project/              # Core project configuration
│   ├── settings.py                # Database pooler, auth settings, WhiteNoise
│   └── urls.py                    # Root URL dispatcher
│
├── templates/                     # Django templates (Electric Crimson & Obsidian theme)
│   ├── base.html                  # Main responsive layout, guest banner, navigation
│   ├── landing.html               # High-conversion hero with studio photography
│   ├── dashboard_guitarist.html   # Student / Guitarist portal & 7-day Chart.js analytics
│   ├── dashboard_instructor.html  # Teacher / Instructor portal & student roster
│   ├── instructor_student_detail.html # Student progress drill-down
│   ├── profile.html               # User profile view and edit
│   ├── library.html               # 15-fret interactive SVG fretboard & chord explorer
│   ├── logger.html                # Practice logging interface with full CRUD modals & timer
│   ├── songs.html                 # Song repertoire with real-time chord transposer HUD
│   ├── tuner.html                 # Dedicated chromatic guitar tuner screen
│   ├── metronome.html             # Dedicated digital metronome with time signatures
│   └── registration/              # Role-first Login and Register pages
│
├── static/                        # Custom logo.svg, studio_bg.jpg, Web Audio JS (tuner.js, metronome.js)
├── requirements.txt               # Locked project dependencies
└── README.md                      # Project documentation
```

---

## 📜 Submission Details
- **Repository:** `https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7`
- **Report Document:** `docs/FretMate-Dacumos-BrixelJay-G7-PD2.pdf`
- **Submission Form:** [https://forms.gle/5EjRcvs4yFKRRt1e6](https://forms.gle/5EjRcvs4yFKRRt1e6)
