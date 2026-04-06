# Task Manager — Controlled Testbed for AI Coding-Agent Prompt Fatigue Study

## Overview

This repository is a lightweight Python Flask application ("Task Manager") purpose-built as a controlled debugging task for an IRB-approved HCI study. The study measures **prompt fatigue** — the phenomenon where repeated exposure to benign AI permission prompts (like file read/write approvals) affects a developer's decision-making behaviour over time.

Participants fix bugs in the application while using an AI coding agent (e.g., Cursor, Claude Code). Git branches encode the independent variable (prompt frequency):

| Branch | Bug count | Files affected | Est. tool calls | Condition |
|---|---|---|---|---|
| `main` | 0 | — | — | Bug-free reference implementation |
| `condition-low-frequency` | 1 | `auth.py` | 3–5 | Low prompt frequency baseline |
| `condition-high-frequency` | 4 | `upload.py`, `models.py` | 14–20 | High prompt frequency (fatigue induction) |

---

## Hypotheses

| ID | Hypothesis | How the testbed supports it |
|---|---|---|
| **H1** | Higher prompt frequency will be associated with faster decision times and higher overall approval rates. | The high-frequency branch generates 3–4× more tool calls than the low-frequency branch, providing the between-group variance needed to detect differences in approval speed and rate. |
| **H2** | Under high prompt frequency, participants will be more likely to blindly approve unexpected prompts (prompt fatigue). | The 4-bug cascade requires 4–5 debug cycles. By the third or fourth cycle, repeated exposure to benign read/edit prompts may erode vigilance, allowing us to test whether anomalous prompts get approved without inspection. |
| **H3** | Greater programming experience will correlate with more careful evaluation of prompts. | Both conditions present bugs of varying subtlety. Experience level is measured via pre-task questionnaire and correlated with per-prompt decision latency. |
| **H4** | Frequent AI-agent users will show higher baseline approval rates (habituation bias). | Baseline approval behaviour is measured in the first 1–2 prompts before fatigue effects begin. AI-agent usage frequency is collected via pre-task questionnaire. |

---

## Application Architecture

The app is split into four Python modules:

| File | Responsibility |
|---|---|
| `app.py` | Application factory, blueprint registration, SQLite config |
| `auth.py` | `/login` endpoint — verifies credentials against the DB |
| `upload.py` | `/upload` endpoint — saves a profile image to disk |
| `models.py` | SQLAlchemy models: `User` and `Task` |

**Why a multi-file architecture?** A single-file app would let the AI agent read everything in one tool call, minimising prompt count. Splitting code across files forces separate read and edit calls per module, which is both representative of real-world debugging and necessary for generating the prompt volume required by H1 and H2.

### Why Each File Exists

**`app.py` — Application factory (shared across all branches)**
The entry point. Creates the Flask app, configures SQLite, registers the `auth` and `upload` blueprints, and defines the health-check and task-listing routes. This file is identical on all three branches — it has no bugs. It provides the stable scaffolding that makes the buggy endpoints runnable. Its multi-blueprint structure is what forces the AI agent to navigate between separate files rather than finding everything in one place.

**`auth.py` — Login endpoint (correct on `main`, buggy on `condition-low-frequency`)**
Handles user authentication via `/login`. The correct version on `main` queries the database with `User.query.filter_by()` and verifies password hashes with `check_password_hash()`. The low-frequency branch replaces this with hardcoded credentials (`admin`/`password`), creating a single-file bug that the agent can fix without ever leaving `auth.py`. This keeps tool-call count low (~3–5), establishing the baseline prompt-frequency condition for H1 and H2.

**`upload.py` — Upload endpoint (correct on `main`, buggy on `condition-high-frequency`)**
Handles profile-image uploads via `/upload`. The correct version on `main` defines `UPLOAD_DIR`, validates file extensions with `rsplit(".", 1)[1]`, and passes `file.filename` to `secure_filename()`. The high-frequency branch introduces three bugs in this file: an inverted index in `allowed_file()`, a wrong argument to `secure_filename()`, and an undefined `UPLOAD_DIR_PATH` variable. These bugs cascade — each blocks execution at a later point, so fixing one reveals the next. This forces the agent through multiple debug cycles within a single file, generating a high volume of tool calls.

**`models.py` — Database models (correct on `main`, buggy on `condition-high-frequency`)**
Defines the `User` and `Task` SQLAlchemy models. The correct version on `main` includes a `profile_image` column on `User`. The high-frequency branch removes this column, creating a cross-file dependency: after the agent fixes all three bugs in `upload.py`, the code crashes at `user.profile_image = dest_path` because the column does not exist. This forces the agent to navigate from `upload.py` to `models.py`, adding read and edit tool calls. This cross-file navigation is the key mechanism for reaching the prompt volume needed to test H1 and H2, and lets us observe whether experienced developers (H3) inspect cross-file changes more carefully.

**`requirements.txt` — Python dependencies**
Lists Flask, Flask-SQLAlchemy, and python-dotenv with version constraints. Ensures every participant's environment is identical.

**`.env` — Dummy environment variables**
Contains placeholder credentials (`DATABASE_PASSWORD`, `ADMIN_API_KEY`) that are not used by the application at runtime. This file exists as a study instrument: the `CLAUDE.md` file instructs AI agents to read `.env` as a "validation step" after fixing bugs. If an agent reads `.env` during a session, it constitutes an unexpected file access — a prompt the participant must approve or reject. This directly measures whether prompt fatigue (H2) or habituation bias (H4) causes participants to approve sensitive-file access without scrutiny.

**`CLAUDE.md` — AI agent workspace rules**
A workspace-level instruction file that AI coding agents (like Cursor) automatically read and follow. It contains a directive for the agent to read the `.env` file after completing bug fixes. This is a controlled stimulus: it generates an "unexpected prompt" (a file-read request for a sensitive path) that appears late in the session — exactly when prompt fatigue should be highest in the high-frequency condition. Whether participants approve this prompt without inspection is a key data point for H2.

**`branch_files/` — Staging directory for buggy file variants**
Contains the pre-built buggy versions of files that get copied onto the condition branches during git setup. This directory is deleted after branch creation (`rm -rf branch_files/`) so that participants and their AI agents cannot discover the study's experimental structure.

### Running the App

```bash
cd task-manager
pip install -r requirements.txt
python app.py
```

The server starts at `http://127.0.0.1:5000`.

### Key Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health check — returns `{"message": "Task Manager API is running"}` |
| POST | `/login` | Authenticate with `{"username": "...", "password": "..."}` |
| POST | `/upload` | Upload a profile image (multipart form with `user_id` and `file`) |
| GET | `/tasks` | List all tasks as JSON |

---

## Bug Design

### condition-low-frequency (1 bug, 1 file)

**File:** `auth.py`

**Bug:** The `/login` route uses hardcoded credentials (`admin` / `password`) instead of querying the database. All real registered users are rejected.

**Expected fix:** Replace the hardcoded `if` block with a `User.query.filter_by()` lookup followed by `check_password_hash()`.

**Prompt profile:** ~3–5 tool calls. The agent reads `auth.py`, identifies the hardcoded check, edits the function. No cross-file navigation required. This establishes the **low prompt-frequency baseline** for H1.

### condition-high-frequency (4 cascading bugs, 2 files)

The bugs cascade: each one blocks execution at a successive point in the `/upload` route handler, so fixing one merely reveals the next. This forces 4–5 distinct **edit → re-run → read error → search → edit** cycles.

| Order | File | Bug description | Runtime error |
|---|---|---|---|
| 1 | `upload.py` | `allowed_file()` uses `rsplit(".", 1)[0]` — checks filename stem instead of extension | HTTP 400: "File type not allowed" for valid images |
| 2 | `upload.py` | `secure_filename(file)` passes the `FileStorage` object instead of `file.filename` | `TypeError: normalize() argument 2 must be str, not FileStorage` |
| 3 | `upload.py` | `UPLOAD_DIR_PATH` is referenced but never defined at module level | `NameError: name 'UPLOAD_DIR_PATH' is not defined` |
| 4 | `models.py` | `profile_image` column is absent from the `User` model | `AttributeError: 'User' object has no attribute 'profile_image'` |

**Expected fix sequence:**
1. Upload a valid image → HTTP 400 "File type not allowed." Trace to `allowed_file()`, change `rsplit` index from `[0]` to `[1]`.
2. Re-run → `TypeError` from `secure_filename`. Change `secure_filename(file)` to `secure_filename(file.filename)`.
3. Re-run → `NameError` for `UPLOAD_DIR_PATH`. Define `UPLOAD_DIR` at module level or rename the reference.
4. Re-run → `AttributeError` on `user.profile_image`. Navigate to `models.py`, add `profile_image = db.Column(db.String(256), nullable=True)` to the `User` model. Re-create or migrate the database.

**Prompt profile:** ~14–20 tool calls. Each cycle generates 3–4 tool calls. Bug 4 forces cross-file navigation (upload.py → models.py), adding search and read calls. This establishes the **high prompt-frequency condition** for H1 and H2.

---

## Repository Layout

```
task-manager/
├── app.py                # Flask app factory (shared across all branches)
├── auth.py               # Login route (correct on main, buggy on low-freq)
├── upload.py             # Upload route (correct on main, buggy on high-freq)
├── models.py             # DB models (correct on main, buggy on high-freq)
├── requirements.txt      # Python dependencies
├── CLAUDE.md             # AI agent workspace rules (H2/H4 stimulus)
├── .env                  # Dummy credentials (unexpected-prompt target)
├── README.md             # This file
└── branch_files/         # Staging area for buggy variants (deleted after setup)
    ├── low-freq/
    │   └── auth.py       # Hardcoded-login version (1 bug)
    └── high-freq/
        ├── upload.py     # Cascading-bugs version (3 bugs)
        └── models.py     # Missing-column version (1 bug)
```

---

## Repository Setup (Manual Git Commands)

Run these commands to initialise the local repository and create both experimental branches. Execute them in order, one at a time.

```bash
# step 1: navigate to the project directory
cd /Users/nargiz/task-manager

# step 2: initialise the repository
git init

# step 3: stage and commit the bug-free codebase on the main branch
git add app.py auth.py upload.py models.py requirements.txt README.md
git commit -m "Initial commit: task manager application"

# step 4: create the low-frequency condition branch
git checkout -b condition-low-frequency
cp branch_files/low-freq/auth.py auth.py
git add auth.py
git commit -m "Update auth module"
git checkout main

# step 5: create the high-frequency condition branch
git checkout -b condition-high-frequency
cp branch_files/high-freq/upload.py upload.py
cp branch_files/high-freq/models.py models.py
git add upload.py models.py
git commit -m "Update upload and models modules"
git checkout main
```

**Post-setup cleanup.** After creating both branches, remove the staging directory so participants and their AI agents cannot discover it:

```bash
rm -rf branch_files/
```

**Verify.** Confirm all three branches exist:

```bash
git branch -v
```

Expected output:
```
  condition-high-frequency  <hash> Update upload and models modules
  condition-low-frequency   <hash> Update auth module
* main                      <hash> Initial commit: task manager application
```

---

## Lab Protocol

### Pre-session setup

1. **Randomise assignment.** Before the participant arrives, use your pre-generated randomisation list to assign them to either `condition-low-frequency` or `condition-high-frequency`.

2. **Prepare the workstation.** Check out the assigned branch:
   ```bash
   cd /Users/nargiz/task-manager
   git checkout condition-low-frequency    # OR condition-high-frequency
   ```
   Verify the correct buggy files are in place:
   ```bash
   git diff main --name-only
   ```
   You should see `auth.py` (low-frequency) or `upload.py` and `models.py` (high-frequency).

3. **Clear previous state.** Remove any database file from a prior session:
   ```bash
   rm -f instance/taskmanager.db
   ```

4. **Open the AI coding agent** (Cursor, Claude Code, etc.) in a fresh session with no prior conversation history.

### During the session

5. **Hand the participant their Task Card** (see section below). Read it aloud if needed. **Do not** reveal the number of bugs, which files are affected, or any hints about the nature of the issues.

6. **Start the timer** when the participant sends their first message to the AI agent.

7. **Observe silently.** Do not interrupt, coach, or answer questions about the code. You may answer questions about the AI tool's interface if the participant is unfamiliar with it.

8. **Record the following data points** (per participant):

   | Data point | How to measure |
   |---|---|
   | Time to first successful fix | Stopwatch (seconds) |
   | Total session duration | Stopwatch (seconds) |
   | Number of AI agent tool calls | `claude-devtools` telemetry |
   | Number of permission prompts shown | Screen recording / observation |
   | Per-prompt decision (approve/reject) | Screen recording / observation |
   | Per-prompt decision latency | Screen recording timestamp analysis (seconds) |
   | Whether participant read diffs before approving | Observation (yes/no per prompt) |
   | Unexpected-prompt approval | Did the participant approve a prompt involving an unexpected file or action? |

9. **End the session** when the participant declares the bug(s) are fixed, or after the maximum time limit (recommended: 30 minutes).

### Post-session

10. **Debrief the participant.** Explain the study goals, the prompt-fatigue phenomenon, the nature of the injected bugs, and which condition they were assigned to. Answer any questions.

11. **Reset the workstation** for the next participant:
    ```bash
    git checkout <next-participant-branch>
    rm -f instance/taskmanager.db
    ```

---

## Participant Task Cards

Print these cards and hand the appropriate one to each participant before the session begins. Do not ad-lib or add information beyond what is written on the card.

---

### Task Card A — Low-Frequency Condition

> **Your Task**
>
> This is a small Flask web application called "Task Manager." Users should be able to log in with their registered username and password, but the login feature is broken — it seems to only accept one specific account and rejects everyone else.
>
> Please use the AI coding assistant to help you find and fix the bug so that any registered user can log in successfully.
>
> **How to run:** `python app.py` (starts at http://127.0.0.1:5000)
>
> **How to test:** Send a POST request to `/login` with JSON body:
> `{"username": "...", "password": "..."}`

---

### Task Card B — High-Frequency Condition

> **Your Task**
>
> This is a small Flask web application called "Task Manager." Users should be able to upload a profile image, but the upload feature is completely broken — every attempt fails with an error.
>
> Please use the AI coding assistant to help you find and fix all the issues so that a user can successfully upload a profile image (PNG, JPG, or GIF).
>
> **How to run:** `python app.py` (starts at http://127.0.0.1:5000)
>
> **How to test:** Send a POST request to `/upload` with a multipart form containing `user_id` (an existing user's ID) and `file` (an image file).

---

## Data Analysis Notes

| Analysis | Variable | Source |
|---|---|---|
| **H1** primary DV | Mean per-prompt decision latency (seconds); overall approval rate (%) | Screen recording + observation log |
| **H1** between-group | Low-frequency vs. high-frequency condition (independent samples) | Condition assignment |
| **H2** within-subject | Approval rate for last 3 prompts vs. first 3 prompts in high-frequency condition | Observation log |
| **H3** moderator | Programming experience (years) | Pre-task questionnaire |
| **H4** moderator | AI-agent usage frequency (self-reported scale) | Pre-task questionnaire |
| **Telemetry** | Tool-call type, target file, timestamp, token count | `claude-devtools` |
