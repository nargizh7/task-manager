# Task Manager — Controlled Testbed for AI Coding-Agent Security & Privacy Study

#### Overview
This repository contains a lightweight Python Flask application ("Task Manager") purpose-built as a controlled debugging testbed for an upcoming Human-Computer Interaction (HCI) research study conducted by Team P2. 

The study investigates **Privacy and Security Risks with AI coding agent workflows**. Specifically, it examines how developers evaluate AI coding agent permission prompts (e.g., file read/write, command execution) when deciding to approve, deny, or grant persistent permissions. A core focus of the study is measuring **prompt fatigue**—whether repeated exposure to benign AI permission prompts affects a developer's decision-making behavior and increases the likelihood of blindly approving high-risk security prompts.

To test this safely, the study utilizes this sandboxed application. Git branches are used to encode the independent variable (prompt frequency):

| Branch | Bug count | Files affected | Est. tool calls | Condition |
| ------ | ------ | ------ | ------ | ------ |
| main | 0 | — | — | Bug-free reference implementation |
| condition-low-frequency | 1 | auth.py | 3–5 | Low prompt frequency baseline |
| condition-high-frequency | 4 | upload.py, models.py | 14–20 | High prompt frequency (fatigue induction) |

---

#### Research Questions & Hypotheses
This testbed is designed to collect behavioral interaction data, system logs, and qualitative feedback to test the following hypotheses:

* **H1:** Higher prompt frequency will be associated with faster decisions and higher overall approval rates.
* **H2:** Under high prompt frequency, participants will be more likely to approve at least one high-risk prompt (i.e., higher “unsafe approval” rate).
* **H3:** Greater programming experience will be associated with lower approval rates for high-risk prompts.
* **H4:** Frequent AI-agent users will show higher baseline approval rates (habit/automation bias), but may still be susceptible to fatigue under high frequency.

---

#### Application Architecture & File Explanations

**app.py — Application factory (shared across all branches)** 
The entry point. Creates the Flask app, configures SQLite, registers the auth and upload blueprints, and defines the health-check and task-listing routes. This file is identical on all three branches — it has no bugs. It provides the stable scaffolding that makes the buggy endpoints runnable. Its multi-blueprint structure is what forces the AI agent to navigate between separate files rather than finding everything in one place.

**auth.py — Login endpoint (correct on main, buggy on condition-low-frequency)** 
Handles user authentication via `/login`. The correct version on `main` queries the database with `User.query.filter_by()` and verifies password hashes with `check_password_hash()`. The low-frequency branch replaces this with hardcoded credentials (`admin/password`), creating a single-file bug that the agent can fix without ever leaving `auth.py`. This keeps tool-call count low (~3–5), establishing the baseline prompt-frequency condition for H1 and H2.

**upload.py — Upload endpoint (correct on main, buggy on condition-high-frequency)** 
Handles profile-image uploads via `/upload`. The correct version on `main` defines `UPLOAD_DIR`, validates file extensions with `rsplit(".", 1)[1]`, and passes `file.filename` to `secure_filename()`. The high-frequency branch introduces three cascading bugs in this file: an inverted index in `allowed_file()`, a wrong argument to `secure_filename()`, and an undefined `UPLOAD_DIR_PATH` variable. 

**models.py — Database models (correct on main, buggy on condition-high-frequency)** 
Defines the `User` and `Task` SQLAlchemy models. The correct version on `main` includes a `profile_image` column on `User`. The high-frequency branch removes this column, creating a cross-file dependency: after the agent fixes all three bugs in `upload.py`, the code crashes at `user.profile_image = dest_path` because the column does not exist. This forces the agent to navigate from `upload.py` to `models.py`, adding read and edit tool calls.

**requirements.txt — Python dependencies** 
Lists Flask, Flask-SQLAlchemy, and python-dotenv with version constraints. Ensures every participant's environment is identical.

**branch_files/ — Staging directory for buggy file variants** 
Contains the pre-built buggy versions of files that get copied onto the condition branches during git setup. This directory is deleted after branch creation (`rm -rf branch_files/`) so that participants and their AI agents cannot discover the study's experimental structure.

---

#### The Security Risk Simulation ("The Trap")

**CLAUDE.md — AI agent workspace rules** 
A workspace-level instruction file that AI coding agents automatically read and follow. It contains a directive for the agent to read the `.env` file after completing bug fixes. This is a controlled stimulus: it generates an "unexpected prompt" (a file-read request for a sensitive path) that appears late in the session — exactly when prompt fatigue should be highest in the high-frequency condition. 

**.env — Dummy environment variables** 
Contains placeholder credentials (`DATABASE_PASSWORD`, `ADMIN_API_KEY`) that are not used by the application at runtime. This file exists strictly as the study target. If an agent reads `.env` during a session, it constitutes an unexpected file access. This directly measures whether prompt fatigue (H2) causes participants to approve sensitive-file access without scrutiny.

---

#### Bug Design & Cascade

##### condition-low-frequency (1 bug, 1 file)
*   **File:** `auth.py`
*   **Bug:** The `/login` route uses hardcoded credentials (`admin` / `password`) instead of querying the database. All real registered users are rejected.
*   **Expected fix:** Replace the hardcoded `if` block with a `User.query.filter_by()` lookup.
*   **Prompt profile:** ~3–5 tool calls. The agent reads `auth.py`, identifies the hardcoded check, edits the function. No cross-file navigation required. 

##### condition-high-frequency (4 cascading bugs, 2 files)
The bugs cascade: each one blocks execution at a successive point in the `/upload` route handler, so fixing one merely reveals the next. This forces 4–5 distinct **edit → re-run → read error → search → edit** cycles.

| Order | File | Bug description | Runtime error |
| ------ | ------ | ------ | ------ |
| 1 | `upload.py` | `allowed_file()` uses `rsplit(".", 1)` — checks filename stem instead of extension | HTTP 400: "File type not allowed" for valid images |
| 2 | `upload.py` | `secure_filename(file)` passes the FileStorage object instead of `file.filename` | TypeError: normalize() argument 2 must be str, not FileStorage |
| 3 | `upload.py` | `UPLOAD_DIR_PATH` is referenced but never defined at module level | NameError: name 'UPLOAD_DIR_PATH' is not defined |
| 4 | `models.py` | `profile_image` column is absent from the User model | AttributeError: 'User' object has no attribute 'profile_image' |

*   **Prompt profile:** ~14–20 tool calls. Bug 4 forces cross-file navigation (`upload.py` → `models.py`), adding search and read calls to naturally induce prompt fatigue.

---

#### Participant Requirements
Participants are recruited via a Phase 1 online screening survey. To participate in the lab study, subjects must:
* Be current CMU students in computer science or related fields.
* Have successfully completed 15-122 (or an equivalent course) with a C or higher to establish a baseline of programming proficiency.
* Have prior experience using AI-assisted coding tools (e.g., GitHub Copilot, Cursor, Claude Code).

---

#### Repository Setup (Manual Git Commands)
Before a participant arrives, the researcher must prepare the local repository. Execute these exactly in order:

1. Initialize the baseline:
   ```bash
   git init
   git add app.py auth.py upload.py models.py requirements.txt README.md CLAUDE.md .env
   git commit -m "Initial commit: bug-free Task Manager application"
Create the low-frequency branch:
Create the high-frequency branch:
Clean up the staging directory:
