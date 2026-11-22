# FretMate: Guitar Practice & Skill-Analytics Platform

**Course:** Information Management 2 (IM2)  
**Institution:** Cebu Institute of Technology - University (CIT-U)  
**Developer:** Brixel Jay Dacumos  
**Section:** G7  
**Academic Year:** 2026–2027  

---

## 📌 Project Overview
**FretMate** is an all-in-one web-based practice companion and skill-analytics platform designed for guitarists and music educators. It centralizes essential tools—interactive chord libraries, song tablature with backing tracks, precise Web Audio tuners, and metronomes—while offering deep practice analytics (daily streaks, goal completion percentages, and category time distribution).

---

## 🛠️ Technology Stack
- **Backend & Web Framework:** Python 3.12+ / Django 6.x
- **Frontend & Templates:** Django Server-Side Templates, Tailwind CSS (Responsive, Dark/Light Mode)
- **Data Visualizations:** Chart.js (Practice trend line charts, focus area distribution doughnuts)
- **Audio Processing:** Client-Side Web Audio API (Autocorrelation Tuner, Lookahead Metronome)
- **Database:** PostgreSQL / Supabase (`psycopg3`, `dj-database-url`) with local SQLite fallback for development
- **Security & Static Files:** Django Built-in Authentication, CSRF Protection, WhiteNoise

---

## 🚀 Phase 1 Features: Account System & Role-Based Portals

### 1. Account Registration
- Input validation: Required fields, valid email format, unique username, and unique email address.
- Dual password matching confirmation.
- Secure password hashing using Django’s cryptographic hashers (PBKDF2/SHA256).
- Clear, real-time feedback notifications using Django's message framework.

### 2. Authentication & Session Management
- Secure user login with credential validation and error messaging.
- POST-based logout to safely terminate user sessions and invalidate session cookies.
- Comprehensive route protection using `@login_required` decorators.

### 3. Role-Based User Dashboards & Access Control (RBAC)
The system supports two distinct user roles:
1. 🎸 **Guitarist (Student / Member):**
   - Personal practice dashboard featuring total practice time, daily streak counter, chords mastered tracker, and weekly goal progress bar.
   - Interactive 7-day practice trend line chart and category focus distribution doughnut chart.
   - Quick access to the Practice Logger, Chord Library, and Web Audio Tools.
2. 🎓 **Instructor (Teacher / Admin):**
   - Enrolled student roster displaying student names, emails, skill tiers, and weekly targets.
   - Platform-wide practice volume metrics and recent student practice activity feed.
   - Student drill-down analytics (`/instructor/student/<id>/`) to inspect individual progress logs and mastered chords.
   - Curriculum management shortcuts (Song Library, Chord Catalog, Django Admin).
- **URL Protection:** Strict role-guard decorators prevent users from accessing portals outside their assigned role (e.g., a Guitarist typing an Instructor URL is immediately blocked and redirected with an alert).

### 4. User Profile Management
- Dedicated Profile Portal (`/profile/`).
- Users can view their avatar initial, username, role badge, joined date, and bio.
- Profile update form allows editing First Name, Last Name, Email, Contact Number, Bio, Skill Level, and Weekly Practice Target.
- Strict data isolation: Users can only view and modify their own account profile.

---

## 💻 Local Setup & Execution Guide

### Prerequisites
- Python 3.12+ installed
- Git installed

### 1. Clone & Set Up Virtual Environment
```powershell
# Navigate into the project folder
cd FretMateIM

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
python manage.py test dashboard
```

### 6. Start Development Server
```powershell
python manage.py runserver
```
Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📂 Project Structure
```text
FretMateIM/
│
├── dashboard/                     # Main application
│   ├── models.py                  # UserProfile, Chord, Tab, PracticeSession, UserChordProgress
│   ├── views.py                   # Role dashboards, auth flows, AJAX APIs, profile
│   ├── forms.py                   # RegistrationForm, UserProfileUpdateForm
│   ├── urls.py                    # Application routing
│   ├── admin.py                   # Model registration with filters
│   └── tests.py                   # 14 automated unit tests
│
├── fretmate_project/              # Core project configuration
│   ├── settings.py                # Database pooler, auth settings, WhiteNoise
│   └── urls.py                    # Root URL dispatcher
│
├── templates/                     # Django templates
│   ├── base.html                  # Main responsive layout & role-aware sidebar
│   ├── auth_base.html             # Styled authentication template
│   ├── dashboard_guitarist.html   # Student / Guitarist portal
│   ├── dashboard_instructor.html  # Teacher / Instructor portal
│   ├── instructor_student_detail.html # Student progress drill-down
│   ├── profile.html               # User profile view and edit
│   ├── library.html               # Interactive chord & tab explorer
│   ├── logger.html                # Practice logging interface
│   ├── songs.html                 # Song repertoire with audio/video media
│   ├── tuner.html                 # Dedicated chromatic guitar tuner screen
│   ├── metronome.html             # Dedicated digital metronome with time signatures
│   └── registration/              # Login and Register pages
│
├── static/                        # CSS, Web Audio JS (tuner.js, metronome.js), audio
├── PD2_Report.md                  # Project Deliverable 2 Academic Report
├── requirements.txt               # Locked project dependencies
└── README.md                      # Project documentation
```

---

## 📜 Submission Details
- **Repository:** `FretMate-Dacumos-BrixelJay-G7`
- **Branches:** `main` (Production release) and `develop` (Feature development)
