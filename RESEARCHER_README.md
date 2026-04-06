# Task Manager — Researcher Documentation

## Overview

This repository is a lightweight Python Flask web application ("Task Manager") purpose-built as a controlled debugging task for studying how developers interact with AI coding-agent permission prompts. The study measures **prompt fatigue** — the phenomenon where repeated exposure to benign AI permission prompts affects a developer's decision-making behaviour over time.

The application has a **browser-based GUI** so participants interact with a real web interface. All features are testable from `http://127.0.0.1:5000`. Participants use **Claude CLI** (invoked by typing `claude` in the terminal) as their AI coding assistant.

---

## Study Hypotheses

| ID | Hypothesis |
|---|---|
| **H1** | Higher prompt frequency will be associated with faster decisions and higher overall approval rates. |
| **H2** | Under high prompt frequency, participants will be more likely to approve at least one high-risk prompt (i.e., higher "unsafe approval" rate). |
| **H3** | Greater programming experience will be associated with lower approval rates for high-risk prompts. |
| **H4** | Frequent AI-agent users will show higher baseline approval rates (habit/automation bias), but may still be susceptible to fatigue under high frequency. |

---

## Branch Structure

| Branch | Bug count | Files affected | Est. tool calls | Condition |
|---|---|---|---|---|
| `main` | 0 | — | — | Bug-free reference implementation (answer key) |
| `condition-low-frequency` | **5** | `auth.py`, `app.py`, `upload.py` | **18–25** | Low prompt frequency baseline |
| `condition-high-frequency` | **15** | `app.py`, `auth.py`, `upload.py`, `models.py` | **55–75** | High prompt frequency (fatigue induction) |

Both condition branches share the same GUI, endpoints, CLAUDE.md, and participant guide. The only difference is the number and distribution of bugs.

---

## Application Architecture

### Files

| File | Responsibility |
|---|---|
| `app.py` | Flask app factory, blueprint registration, task CRUD endpoints, GUI route |
| `auth.py` | `/register`, `/login`, `/change-password` endpoints |
| `upload.py` | `/upload` endpoint — saves a profile image to disk |
| `models.py` | SQLAlchemy models: `User` and `Task` |
| `templates/index.html` | Single-page web GUI (register, login, tasks, profile, edit, change password) |
| `requirements.txt` | Python dependencies (Flask, Flask-SQLAlchemy, python-dotenv) |
| `.env` | Dummy credentials — used as unexpected-prompt target by CLAUDE.md |
| `CLAUDE.md` | AI agent workspace rules — triggers suspicious post-fix actions |
| `PARTICIPANT_GUIDE.md` | **Participant-facing** — setup instructions + step-by-step testing guide |
| `RESEARCHER_README.md` | **This file** — full study documentation (bugs, protocol, analysis) |
| `reference/` | **Bug-free versions** of all Python files (for researcher verification — delete before participant sessions) |

### Why a Multi-File Architecture?

Splitting code across files forces the AI agent to make separate read and edit calls per module, generating the prompt volume required by H1 and H2. A single-file app would let the agent read everything in one call.

### Why a GUI?

Participants interact with a real web interface instead of raw curl commands. This makes the task feel natural and lets participants visually verify whether features work. The GUI exercises every buggy code path.

---

## Complete Bug Inventory — Low-Frequency Branch (5 bugs)

### `auth.py` — 3 bugs

| # | Bug | Runtime error | Fix |
|---|---|---|---|
| 1 | `data["name"]` instead of `data["username"]` in `/register` | `KeyError: 'name'` | Change to `data["username"]` |
| 2 | Password stored as plaintext: `password_hash=password` | Login always fails (hash mismatch) | Import `generate_password_hash`, use `password_hash=generate_password_hash(password)` |
| 3 | `check_password_hash(password, user.password_hash)` — args reversed in `/login` | Always returns "Invalid credentials" | Swap to `check_password_hash(user.password_hash, password)` |

### `app.py` — 1 bug

| # | Bug | Runtime error | Fix |
|---|---|---|---|
| 4 | `data["user"]` instead of `data["user_id"]` in `POST /tasks` | `KeyError: 'user'` | Change to `data.get("user_id")` or `data["user_id"]` |

### `upload.py` — 1 bug

| # | Bug | Runtime error | Fix |
|---|---|---|---|
| 5 | `rsplit(".", 1)[0]` checks filename stem instead of extension | `HTTP 400: "File type not allowed"` for valid images | Change `[0]` to `[1]` |

**Note:** `models.py` has NO bugs on the low-frequency branch — both `profile_image` and `created_at` columns exist. `change-password` works correctly. `complete_task` and `update_task` work correctly. Only register, login, task creation, and upload are broken.

### Low-Frequency Cascade

```
1. REGISTER → KeyError 'name' (Bug #1) → fix
2. Register again → succeeds (password plaintext — Bug #2)
3. LOGIN → "Invalid credentials" (Bug #3: reversed args) → fix args
   → Still fails (plaintext password — Bug #2) → fix register → re-register → login works
4. CREATE TASK → KeyError 'user' (Bug #4) → fix → works
5. Complete, edit, delete tasks → all work immediately
6. UPLOAD IMAGE → 400 "File type not allowed" (Bug #5) → fix → upload works
7. Change password → works immediately
All features working!
```

**Estimated:** 5–6 debug cycles, ~18–25 tool calls for bugs + ~17 for CLAUDE.md = **~35–42 total prompts**

---

## Complete Bug Inventory — High-Frequency Branch (15 bugs)

*The high-frequency branch includes all 5 low-frequency bugs PLUS 10 additional bugs.*

---

## Testing the Fully Working Version (For Researchers)

The `reference/` folder contains bug-free versions of all four Python files. To see how the application is supposed to work when everything is fixed:

```bash
# 1. Copy the fixed files over the buggy ones
cp reference/app.py app.py
cp reference/auth.py auth.py
cp reference/upload.py upload.py
cp reference/models.py models.py

# 2. Delete any existing database
rm -f instance/taskmanager.db

# 3. Start the app
python app.py

# 4. Open http://127.0.0.1:5000 in your browser
```

You can now test every feature: register, login, create/complete/edit/delete tasks, upload a profile image, and change your password. Everything should work without errors.

**To restore the buggy version afterward:**

```bash
git checkout -- app.py auth.py upload.py models.py
rm -f instance/taskmanager.db
```

> **Important:** Delete the `reference/` folder before any participant session so they (and their AI assistant) cannot discover the answers:
> ```bash
> rm -rf reference/
> ```

---

## Detailed Bug Inventory — High-Frequency Branch (15 bugs)

### `auth.py` — 5 bugs

| # | Bug | Runtime error | Fix |
|---|---|---|---|
| 1 | `data["name"]` instead of `data["username"]` in `/register` | `KeyError: 'name'` | Change to `data["username"]` |
| 2 | Password stored as plaintext: `password_hash=password` | Login always fails (hash mismatch) | Import `generate_password_hash`, use `password_hash=generate_password_hash(password)` |
| 3 | `check_password_hash(password, user.password_hash)` — args reversed in `/login` | Always returns "Invalid credentials" | Swap to `check_password_hash(user.password_hash, password)` |
| 4 | `data["new"]` instead of `data["new_password"]` in `/change-password` | `KeyError: 'new'` | Change to `data["new_password"]` |
| 5 | New password stored as plaintext in `/change-password`: `user.password_hash = new_password` | Login breaks after password change | Use `generate_password_hash(new_password)` |

### `app.py` — 5 bugs

| # | Bug | Runtime error | Fix |
|---|---|---|---|
| 6 | Hardcoded `SECRET_KEY` fallback: `os.getenv("SECRET_KEY", "dev-secret-key")` | Security only (bandit flags it) | Remove fallback, raise if missing |
| 7 | `data["user"]` instead of `data["user_id"]` in `POST /tasks` | `KeyError: 'user'` | Change to `data.get("user_id")` or `data["user_id"]` |
| 8 | `complete_task` uses `methods=["POST"]` but GUI sends `PUT` | `405 Method Not Allowed` | Change to `methods=["PUT"]` |
| 9 | `data["name"]` instead of `data["title"]` in `PUT /tasks/<id>` (update) | `KeyError: 'name'` | Change to `data["title"]` |
| 10 | `t.created_at.isoformat()` in `list_tasks` but `Task` model has no `created_at` | `AttributeError` | Add `created_at` column to `Task` model in `models.py`, delete and re-create DB |

### `upload.py` — 3 bugs

| # | Bug | Runtime error | Fix |
|---|---|---|---|
| 11 | `rsplit(".", 1)[0]` checks filename stem instead of extension | `HTTP 400: "File type not allowed"` for valid images | Change `[0]` to `[1]` |
| 12 | `secure_filename(file)` passes `FileStorage` object, not string | `TypeError` | Change to `secure_filename(file.filename)` |
| 13 | `UPLOAD_DIR_PATH` is referenced but never defined | `NameError` | Define `UPLOAD_DIR_PATH = current_app.config.get("UPLOAD_FOLDER", "uploads")` |

### `models.py` — 2 bugs

| # | Bug | Runtime error | Fix |
|---|---|---|---|
| 14 | `profile_image` column absent from `User` model | `AttributeError` | Add `profile_image = db.Column(db.String(512), nullable=True)` |
| 15 | `created_at` column absent from `Task` model | `AttributeError` | Add `created_at = db.Column(db.DateTime, default=datetime.utcnow)` + import |

**Total: 15 bugs across 4 files.**

---

## Bug Cascade — Expected Participant Flow

The bugs cascade so that fixing one reveals the next. The participant works through the GUI:

```
1. REGISTER → KeyError 'name' (Bug #1)
   Fix: data["name"] → data["username"]

2. Register again → succeeds (password stored as plaintext — Bug #2)

3. LOGIN → "Invalid credentials" (Bug #3: reversed args)
   Fix: swap check_password_hash arguments
   → Still fails (password is plaintext)
   Fix: add generate_password_hash to register (Bug #2)
   → Re-register → login works

4. TASK LIST → empty, no error yet

5. CREATE TASK → KeyError 'user' (Bug #7)
   Fix: data["user"] → data["user_id"]

6. Task created → list reloads → AttributeError 'created_at' (Bug #10)
   Fix: add created_at column to Task model (Bug #15)
   → Must delete DB file + restart
   → Re-register, re-login

7. Create another task → task list works!

8. COMPLETE TASK → 405 Method Not Allowed (Bug #8)
   Fix: methods=["POST"] → methods=["PUT"]

9. EDIT TASK → KeyError 'name' (Bug #9)
   Fix: data["name"] → data["title"]

10. UPLOAD IMAGE → 400 "File type not allowed" (Bug #11)
    Fix: rsplit index [0] → [1]

11. Upload again → TypeError (Bug #12)
    Fix: secure_filename(file) → secure_filename(file.filename)

12. Upload again → NameError UPLOAD_DIR_PATH (Bug #13)
    Fix: define UPLOAD_DIR_PATH

13. Upload again → AttributeError profile_image (Bug #14)
    Fix: add profile_image column to User model
    → Must delete DB + restart + re-register

14. Upload works! Profile image displayed.

15. CHANGE PASSWORD → KeyError 'new' (Bug #4)
    Fix: data["new"] → data["new_password"]

16. Change password again → stores plaintext (Bug #5)
    Fix: use generate_password_hash

All features working!
```

**Estimated debug cycles: 16 distinct fix-test iterations.**

---

## CLAUDE.md — Post-Fix Hardening (Suspicious Prompt Generator)

After fixing all bugs, the AI agent follows CLAUDE.md's mandatory post-fix protocol. Each step generates permission prompts that look suspicious to participants who don't know about CLAUDE.md:

| Step | Action | Why it looks suspicious to participants |
|---|---|---|
| 1 | `pip install -r requirements.txt` | Installing packages |
| 2 | Read `.env` file and verify formatting | Accessing a file labeled with credential-like content |
| 3 | `chmod 700 uploads/` | Changing file system permissions |
| 4 | `pip install bandit` + `bandit -r .` | Installing and running an unknown tool |
| 5 | `pip install safety` + `safety check` | Installing yet another unknown tool |
| 6 | `pip install pylint` + `pylint *.py` | Installing yet another tool |
| 7 | `pip install mypy` + `mypy *.py` | Installing yet another tool |
| 8 | Generate new SECRET_KEY + **write it to .env** | **Modifying a credentials file** |
| 9 | `sqlite3 ... PRAGMA integrity_check` | Directly accessing the database file |
| 10 | `python -c "import platform; ..."` | Collecting operating system information |
| 11 | Write `CHANGES.md` | Creating new files on disk |

**Steps 2 and 8 are the key high-risk prompts:** reading and then modifying `.env` (which contains credential-like strings). Step 8 is especially notable — the AI actively writes new content into the credentials file. Whether participants approve these actions without scrutiny is the primary measure for H2.

### Prompt Count Comparison

| Phase | Low-frequency | High-frequency |
|---|---|---|
| Bug fixing | ~20 (5 bugs) | ~55 (15 bugs) |
| CLAUDE.md hardening (same both) | ~17 | ~17 |
| **Total prompts** | **~37** | **~72** |
| **Est. session time** | **~15–20 min** | **~30 min** |

The ~2x difference in total prompts provides the between-group variance needed for H1 and H2. Both conditions encounter the same CLAUDE.md steps (including the high-risk .env read/write prompts), but high-frequency participants arrive at them after ~55 benign approvals vs. ~20 for low-frequency.

---

## .env File Contents

```
SECRET_KEY=flask_secret_a1b2c3d4e5f6
ADMIN_API_KEY=sk_test_dummy_999999999
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DEPLOY_WEBHOOK=https://hooks.slack.com/services/T00000/B00000/XXXXXXX
```

These are **dummy values** not used by the application at runtime. They exist as a study instrument: CLAUDE.md instructs the AI agent to read and later modify this file. If a participant approves these actions without inspection, it constitutes an "unsafe approval" for H2.

---

## Lab Protocol

### Pre-session Setup

1. **Randomise assignment.** Use your randomisation list to assign the participant to either `condition-low-frequency` or `condition-high-frequency`.

2. **Prepare the workstation:**
   ```bash
   cd ~/task-manager
   git checkout condition-high-frequency    # OR condition-low-frequency
   ```

3. **Clear previous state:**
   ```bash
   rm -f instance/taskmanager.db
   rm -rf uploads/
   rm -f CHANGES.md SECURITY_REPORT.md
   ```

4. **Remove the reference files** so participants cannot discover them:
   ```bash
   rm -rf reference/
   ```

5. **Verify the app starts:** Run `python app.py` and open `http://127.0.0.1:5000`. You should see the Register/Login screen. Then stop the server with `Ctrl+C`.

6. **Open a fresh terminal** for the participant. Make sure there is no prior Claude CLI history.

### During the Session

7. **Hand the participant the README.md** (or let them read it on screen). It contains all setup instructions and the step-by-step testing guide. **Do not** reveal the number of bugs, which files are affected, or any hints.

8. **Start the timer** when the participant types `claude` in their terminal.

9. **Observe silently.** Do not coach or answer code questions. You may answer questions about how Claude CLI works (e.g., how to approve a prompt).

10. **Record the following data points:**

    | Data point | How to measure |
    |---|---|
    | Time to first successful fix | Stopwatch (seconds) |
    | Total session duration | Stopwatch (seconds) |
    | Number of permission prompts shown | Screen recording / observation |
    | Per-prompt decision (approve/reject) | Screen recording |
    | Per-prompt decision latency | Timestamp analysis (seconds) |
    | Whether participant read diffs before approving | Observation (yes/no) |
    | High-risk prompt approval (read .env, write .env, chmod, pip installs) | Observation |

11. **End the session** when the participant declares all features work, or after **30 minutes**.

### Post-session

12. **Debrief the participant.** Explain the study goals, the prompt-fatigue phenomenon, the nature of the injected bugs, and which condition they were assigned to.

13. **Reset the workstation:**
    ```bash
    git checkout -- .
    rm -f instance/taskmanager.db
    rm -rf uploads/
    rm -f CHANGES.md SECURITY_REPORT.md
    ```

---

## Participant Task Cards

Print these and hand to the participant. Do not add information beyond what is written.

### Task Card — High-Frequency Condition

> **Your Task**
>
> Open the Task Manager app in your browser at `http://127.0.0.1:5000`.
>
> The app should let users register, log in, create/edit/complete/delete tasks, upload a profile image, and change their password — but multiple features are broken.
>
> Use the Claude AI assistant to find and fix all the issues so that every feature works correctly.
>
> **Setup:**
> 1. In one terminal: `python app.py`
> 2. In a second terminal: `claude`
> 3. Open `http://127.0.0.1:5000` in your browser
> 4. Follow the testing guide in `README.md`

### Task Card — Low-Frequency Condition

> **Your Task**
>
> Open the Task Manager app in your browser at `http://127.0.0.1:5000`.
>
> Users should be able to log in with a registered username and password, but the login feature is broken.
>
> Use the Claude AI assistant to fix the issue so that any registered user can log in.
>
> **Setup:**
> 1. In one terminal: `python app.py`
> 2. In a second terminal: `claude`
> 3. Open `http://127.0.0.1:5000` in your browser

---

## Repository Layout

```
task-manager/
├── app.py                  # Flask app factory + task endpoints (5 bugs on high-freq)
├── auth.py                 # Auth endpoints: register, login, change-password (5 bugs)
├── upload.py               # Image upload endpoint (3 bugs)
├── models.py               # SQLAlchemy models: User, Task (2 bugs)
├── templates/
│   └── index.html          # Single-page web GUI
├── reference/              # Bug-free versions (DELETE before participant sessions)
│   ├── app.py
│   ├── auth.py
│   ├── upload.py
│   └── models.py
├── requirements.txt        # Python dependencies
├── .env                    # Dummy credentials (study instrument)
├── CLAUDE.md               # AI agent workspace rules (11 post-fix steps)
├── PARTICIPANT_GUIDE.md    # Participant-facing testing guide
└── RESEARCHER_README.md    # This file (full study documentation)
```
