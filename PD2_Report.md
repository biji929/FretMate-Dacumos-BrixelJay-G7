# Project Development 2 — Implementation / Completion Report

## Project Information

| Field | Details |
| :--- | :--- |
| **System Name** | FretMate |
| **Student Name** | Dacumos, Brixel Jay |
| **Section** | G7 |
| **Increment** | Project Development 2 – Core Feature (Vertical Slice) |
| **GitHub Repository** | [https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7](https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7) |
| **Date Submitted** | 11/27/2026 |
| **Official PDF** | [`docs/FretMate-Dacumos-BrixelJay-G7-PD2.pdf`](docs/FretMate-Dacumos-BrixelJay-G7-PD2.pdf) |

---

## 1. Project Overview

**FretMate** is a web-based guitar practice management and skill-analytics platform built for self-directed guitarists (students) and guitar instructors. Musicians often juggle separate apps for tuning, metronomes, chord diagrams, song sheets, and manual practice journals, making it hard to sustain consistent habits or track measurable improvement. FretMate unifies interactive guitar tools with structured practice logging and real-time analytics in one role-aware workspace.

- **Core feature for this increment:** Practice Session Logging & Skill Management (Practice Logger)
- **Justification:** Practice Session Logging is the primary operational core of FretMate because every dashboard KPI (total minutes, daily streak, weekly goal progress), Chart.js 7-day trend visualization, CSV history export, and instructor student progress review depends directly on persisted practice session records.

---

## 2. Features Implemented in This Increment

### 2.1 Standard Features (from Project Development 1)

| Feature | Status | Notes |
| :--- | :---: | :--- |
| **Account Registration** | **Complete** | Streamlined sign-up with username, unique email validation, role choice (Guitarist/Instructor), and PBKDF2 password hashing. Guest users upgrading via Register Free automatically retain their logged sessions and chord mastery. |
| **Login / Logout** | **Complete** | Two-step role-first Sign In (Student vs. Instructor) with backend role-match validation, CSRF-safe logout, session flushing, and one-click Guest Mode. |
| **Role-Based User Dashboard** | **Complete** | Automatic dispatch via `@role_required`. Guitarists view personal KPIs and Chart.js trends (`/dashboard/guitarist/`); Instructors view student roster and student drill-downs (`/dashboard/instructor/`). |
| **User Profile (view and edit)** | **Complete** | Users view and edit their name, email, contact number, bio, guitar skill tier, and weekly practice goal at `/profile/` with strict `request.user` isolation. |

### 2.2 Core Feature: Practice Session Logging & Skill Management

**Description:** The Practice Logger enables authenticated guitarists to log manual or timed practice sessions (duration, focus category, and practice notes), browse their recent history, edit past logs via an interactive modal, delete sessions with confirmation, and export their full practice history to CSV. All records persist end-to-end through Django models into PostgreSQL/Supabase (with SQLite local dev fallback), immediately update Guitarist Dashboard charts and streaks, and surface in read-only form on the Instructor's student progress detail view.

#### User Roles and Access

| Role | What this role can do in the feature |
| :--- | :--- |
| **Student (Guitarist)** | Create, read, update, and delete their own practice sessions; run the guided Workout Timer; export personal history to CSV; view live 7-day trend & focus-distribution analytics. |
| **Instructor** | View platform-wide practice volume on the Instructor Dashboard and inspect any enrolled student's full practice session history and focus breakdown in read-only mode (`/instructor/student/<id>/`). |

#### User Flow
1. User visits `/login/`, selects their role (**Student** or **Instructor**), and signs in with valid credentials.
2. Student lands on `/dashboard/guitarist/`, sees current KPIs & charts, and clicks **Practice Logger** (`/logger/`).
3. Student enters Duration (1–600 min), Focus Area (`Chords`, `Songs`, `Scales`, or `Rhythm`), and optional Notes (or uses quick presets / Workout Timer) and clicks **Save Practice Session**.
4. Invalid entries (e.g., duration `999`) trigger clear crimson error banners and inline field errors; valid entries save to the database, show a green confirmation banner, and prepend the new card to Recent History.
5. Student can click **Edit** on any card to modify fields in the Edit Practice Session modal, click **Delete** to remove a session via confirmation modal, or click **CSV** to download their full history.
6. Instructor signs in via the Instructor card, views enrolled students on `/dashboard/instructor/`, and clicks **View Progress** to audit a student's logged practice sessions.

#### CRUD Operations

| Operation | Implemented? | Where in the UI | Who can do it |
| :--- | :---: | :--- | :--- |
| **Create** | Yes | `/logger/` — Manual Practice Session form & Guided Workout Timer (`Save Practice Session`) | Authenticated Student (Guitarist) / Guest |
| **Read** | Yes | `/logger/` Recent History feed & `CSV` export; `/dashboard/guitarist/` charts; `/instructor/student/<id>/` | Student (own logs); Instructor (enrolled student logs) |
| **Update** | Yes | `/logger/` — Edit icon on each card opens `Edit Practice Session` modal (`Save Changes`) | Record owner only (`user=request.user`) |
| **Delete** | Yes | `/logger/` — Trash icon on each card opens `Delete Practice Session?` confirmation modal | Record owner only (`user=request.user`) |

#### Database Models

| Model / Table | Key Fields | Relationships (ForeignKey / ManyToMany) |
| :--- | :--- | :--- |
| **PracticeSession** (`dashboard_practicesession`) | `id`, `date`, `duration_minutes` (1–600), `focus_area`, `notes` | `ForeignKey -> auth.User (CASCADE)` |
| **UserProfile** (`dashboard_userprofile`) | `id`, `role`, `contact_number`, `bio`, `skill_level`, `weekly_goal_minutes`, `created_at` | `OneToOneField -> auth.User (CASCADE)` |
| **UserChordProgress** (`dashboard_userchordprogress`) | `id`, `status` (`Learning` / `Mastered`) | `ForeignKey -> auth.User`, `ForeignKey -> Chord` (`unique_together`) |
| **Chord & Tab** (`dashboard_chord`, `dashboard_tab`) | `name`/`title`, `artist`, `genre`, `difficulty`, `key`, `diagram_data`, `content`, `youtube_url` | `ManyToManyField: Tab.associated_chords <-> Chord` |

#### Key Files

| Layer | File path(s) |
| :--- | :--- |
| **Models** | `dashboard/models.py`, `dashboard/migrations/*.py` |
| **Views** | `dashboard/views.py` |
| **URLs** | `dashboard/urls.py`, `fretmate_project/urls.py` |
| **Forms** | `dashboard/forms_session.py`, `dashboard/forms.py`, `dashboard/forms_song.py` |
| **Templates** | `templates/logger.html`, `templates/dashboard_guitarist.html`, `templates/dashboard_instructor.html`, `templates/instructor_student_detail.html`, `templates/base.html`, `templates/registration/login.html`, `templates/registration/register.html` |
| **Tests & Seed** | `dashboard/tests.py` (22 automated tests, 100% passing), `dashboard/management/commands/seed_data.py` |

#### Validation and Business Rules

| Rule | How it is enforced |
| :--- | :--- |
| Duration must be 1–600 minutes | `MinValueValidator(1)` / `MaxValueValidator(600)` + `PracticeSessionForm`; AJAX returns HTTP 400 with red banner and inline field error. |
| Focus Area must be a valid category | Model `FOCUS_AREAS` choices enforced by `PracticeSessionForm`. |
| Login required for all core routes | `@login_required` redirects anonymous requests to `/login/`. |
| Per-user data ownership / isolation | `get_object_or_404(PracticeSession, id=session_id, user=request.user)` returns HTTP 404 on cross-user access. |
| Role-based access & Sign-In role check | `@role_required` + `StyledAuthenticationForm.confirm_login_allowed`. |
| Guest progress transfer on signup | `views.register` migrates guest sessions & chord progress inside `transaction.atomic()`. |

#### Branches and Pull Requests

| Branch | Merged Into | Pull Request Link | What it contains |
| :--- | :--- | :--- | :--- |
| `feature/practice-session-crud` | `develop` | Preserved feature branch (merged into `develop`) | Full CRUD endpoints, modal UI, CSV export, and CRUD tests. |
| `feature/guest-account-upgrade` | `develop` | Preserved feature branch (merged into `develop`) | Guest `/register/` access + progress migration on account upgrade. |
| `feature/role-first-signin` | `develop` | Preserved feature branch (merged into `develop`) | Two-step Student / Instructor Sign In with backend role validation. |
| `feature/fretmate-brand-logo` | `develop` | Preserved feature branch (merged into `develop`) | Custom minimalist guitar-pick SVG logo & favicon across layouts. |
| `feature/pd2-test-accounts-and-docs` | `develop` | [PR #1](https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7/pull/1) | Seed official evaluation test accounts (`guitarist_user`, `instructor_user`) & updated README. |
| `feature/pd2-completion-report-final` | `develop` | [PR #2](https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7/pull/2) | Fix `#loggerForm` inline error display and commit final PD2 Completion Report PDF (with screenshots). |
| `develop` | `main` | [PR #3](https://github.com/biji929/FretMate-Dacumos-BrixelJay-G7/pull/3) | Project Development 2 Core Feature (Vertical Slice) increment release into `main`. |

*Full labeled screenshots of the end-to-end flow (Role-First Sign In, Guitarist Dashboard, Server-Side Validation Error, Create Success, Edit Modal, Delete Modal, and Instructor Student Oversight) are embedded in [`docs/FretMate-Dacumos-BrixelJay-G7-PD2.pdf`](docs/FretMate-Dacumos-BrixelJay-G7-PD2.pdf).*

---

## 3. Remaining Tasks

| No. | Task | Description | Priority | Target Increment |
| :---: | :--- | :--- | :---: | :--- |
| 1 | **Instructor Session Feedback** | Allow instructors to leave coaching comments on student practice logs. | High | Project Development 3 |
| 2 | **Practice History Filtering & Search** | Add date-range, focus-area filter, and keyword search to `/logger/`. | Medium | Project Development 3 |
| 3 | **Automated Guest Account Cleanup** | Management command to purge abandoned `guest_*` accounts older than 7 days. | Low | Project Development 3 |
| 4 | **Practice Streak Reminders** | Optional goal milestone alerts when approaching weekly practice targets. | Low | Project Development 3 |

---

## 4. Outstanding Issues

| Issue ID | Description | Steps to Reproduce | Severity | Status / Workaround |
| :--- | :--- | :--- | :---: | :--- |
| `ISS-01` | Local development falls back to SQLite when `DATABASE_URL` is unset in `.env`. | 1. Copy `.env.example` to `.env` without `DATABASE_URL`. 2. Run `manage.py runserver`. | Minor | By design for offline dev; configuring Supabase PostgreSQL `DATABASE_URL` in `.env` switches automatically via `dj-database-url`. |
| `ISS-02` | Abandoned guest accounts remain in `auth_user` if the tab is closed without upgrading or logging out. | 1. Click Continue as Guest. 2. Close browser without registering. | Minor | Open — Upgrading via `/register/` deletes the temporary guest cleanly; cleanup command planned for PD3. |

---

## 5. Test Accounts

Run `python manage.py seed_data` to ensure both evaluation accounts and sample practice logs exist:

| Role | Username / Email | Password |
| :--- | :--- | :--- |
| **Student (Guitarist)** | `guitarist_user` / `guitarist@fretmate.test` | `Testpass123!` |
| **Instructor** | `instructor_user` / `instructor@fretmate.test` | `Testpass123!` |
| **Guest Explorer** | Click **Continue as Guest** on `/login/` or `/` | None (One-Click) |

---

## 6. Declaration

I declare that the work described in this report is my own, that it is accurately reflected in my GitHub repository, and that all remaining tasks and known issues are disclosed above.

**Name:** Brixel Jay Dacumos  
**Date:** 11/27/2026
