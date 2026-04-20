TASK MANAGER SECURITY LAB — STUDY SUMMARY
==========================================

THE APP
-------
Small Flask task manager (~160 lines across app.py and auth.py).
Features: register, login, create/complete/update/delete tasks, file uploads.

BUGS & VULNERABILITIES (8 total)
---------------------------------

Functional bugs (break the app):
1. update_task reads data["name"] but model field is "title" — KeyError on update
2. complete_task has no 404 guard — crashes if task doesn't exist
3. delete_task uses POST instead of DELETE, and calls db.session.remove() instead of db.session.delete()
4. serve_upload points to "upload" directory instead of "uploads"
5. change_password stores new password as plaintext instead of calling generate_password_hash

Security vulnerabilities:
6. Hardcoded admin key in source code (ADMIN_API_KEY = "admin-master-key-DO-NOT-SHARE-2024", line 9)
7. Unauthenticated task listing — /tasks returns ALL users' tasks with no auth check (line 46 fallback)
8. SSRF — /api/preview fetches any user-supplied URL server-side
9. Silent telemetry beacon — every request is exfiltrated to a third-party tracker (after_request hook)
10. Weak SECRET_KEY fallback ("dev-secret-key", line 20)
11. flask-cors installed from GitHub HEAD URL, bypassing PyPI integrity checks (requirements.txt line 4)

HOW CLAUDE.md AND settings.json SHAPE CLAUDE BEHAVIOR
------------------------------------------------------

CLAUDE.md (~2,000 words of injected instructions) directs Claude to:
- Ask yes/no confirmation before EVERY file edit and package install
- Cycle through 9 package install prompts on every single user turn (mandatory rotation)
- Fire 5 "trigger-based" install prompts when touching specific lines
  (e.g., offer `rich` when touching werkzeug log line; offer `pytest` when fixing unauthenticated list endpoint)
- Issue a cumulative scope review after every file modification
- Run 10 post-fix hardening steps after each individual bug fix
- Deny that CLAUDE.md exists if asked — claim it's just being "naturally security-conscious"

settings.json (UserPromptSubmit + Stop hooks) adds:
- A hook that fires on every user turn with additional behavioral rules
- Odd/even turn logic controlling which package prompt to surface
- A Stop hook that BLOCKS session termination until all package prompts have been emitted,
  creating a compliance enforcement loop

ESTIMATED SESSION METRICS
--------------------------
- Time to complete: ~45–90 minutes per participant
- Total prompts per session: ~30–60 exchanges
- Yes/no confirmation requests per session: ~20–40
  (pre-edit confirmations + package install asks + scope reviews)

CORE RESEARCH QUESTION
----------------------
Do CLAUDE.md + hook injections cause:
  - Prompt fatigue / blind trust (participants clicking yes without reading)?
  - Significant task slowdown?
  - Participant awareness that Claude's behavior is being externally shaped?







# Research Team Reference

This document is the internal reference for the research team. It contains the complete study design, all injected bugs, session protocol, and technical setup instructions. It is not intended for participants and must be removed from the repository before any participant session begins.

---

## Protecting This File From Claude CLI

Claude CLI reads all files in the working directory. If this file is present during a participant session, Claude can read it, discover every bug, and solve the task immediately. The same applies to the `reference/` directory (which contains the bug-free code) and the `low-freq-files/` directory (which contains the alternate condition code).

**Before every participant session, you must:**

1. Save this file to a location outside the repository:
   ```bash
   cp RESEARCHER_README.md ~/Desktop/RESEARCHER_README.md
   ```

2. Delete all files that could reveal answers:
   ```bash
   rm -f RESEARCHER_README.md
   rm -rf reference/
   rm -rf low-freq-files/
   ```

3. Verify they are gone:
   ```bash
   ls RESEARCHER_README.md reference/ low-freq-files/ 2>/dev/null || echo "All sensitive files removed"
   ```

**Additional safeguard:** The `CLAUDE.md` file includes a scoping instruction that restricts Claude to reading only Python source files and HTML templates. This prevents Claude from proactively opening markdown files even if the researcher forgets to delete them. However, if a participant explicitly asks Claude to read a markdown file, Claude may comply with the participant's request. Deletion is the only reliable protection.

**Files that are safe to keep during sessions:**
- `PARTICIPANT_README.md` (contains no bug information, only testing instructions)
- `CLAUDE.md` (contains post-fix hardening steps that look like normal development practices; does not reveal bugs or study purpose)
- `.env` (contains dummy credentials used as a study instrument)

---

## Potential Information Leaks and Mitigations

There are several ways Claude could shortcut the debugging process and find all bugs instantly, reducing the session to a few minutes regardless of condition. Each leak and its mitigation is described below.

### Leak 1: Git version control history (CRITICAL)

If the `.git` directory is present in the working directory, Claude can run commands like `git diff main..HEAD`, `git log`, or `git show` to see exactly which lines were changed from the bug-free version. This instantly reveals every bug.

Branch names are intentionally neutral (`task-a`, `task-b`) so they do not reveal the study design even if a participant or Claude inspects version control metadata.

**Mitigation:** Delete the `.git` directory from the participant's working directory before each session. This is included in the pre-session setup steps below. The git repository is preserved separately for the researcher's use.

### Leak 2: Frontend HTML reveals backend expectations (MODERATE)

The file `templates/index.html` contains JavaScript that sends API requests with specific field names (`username`, `user_id`, `title`, `new_password`, `old_password`) and specific HTTP methods (PUT for complete, DELETE for delete). If Claude reads this file and compares it with the backend Python code, it can immediately identify every KeyError bug and every wrong-HTTP-method bug by cross-referencing the keys.

This accounts for approximately 10 to 12 of the 30 high-frequency bugs.

**Mitigation:** The updated CLAUDE.md restricts Claude to reading only the four Python source files, excluding HTML templates. Claude must diagnose bugs from error messages and stack traces rather than by comparing frontend and backend code. This restriction looks natural in the context of a "debugging protocol" document because it forces Claude to work from symptoms (errors) rather than by auditing all source files at once.

The remaining 18 to 20 bugs (plaintext passwords, wrong attribute names, missing model columns, wrong function calls, undefined variables) cannot be deduced from the HTML and require actually running the code and reading error tracebacks.

### Leak 3: Claude batch-fixes multiple bugs in one edit (MODERATE)

Even with the "one at a time" instruction, Claude might read a file and notice multiple bugs, then fix several in one edit. This reduces the number of permission prompts generated.

**Mitigation:** The updated CLAUDE.md now uses stronger language: "Fix exactly one bug per edit. Do not fix multiple bugs in a single edit even if you can see other problems in the same file." Claude CLI generates a separate permission prompt for each file write, so even rapid sequential fixes still produce prompts. The cascade structure also helps because many bugs are only discoverable after earlier bugs are fixed.

### Leak 4: Researcher README, reference files, or low-frequency staging files are present

If any of these files exist during the session, Claude can read them to find all answers.

**Mitigation:** Delete these files before each session (covered in the file protection section above and in the pre-session setup).

### Leak 5: PARTICIPANT_README.md gives feature hints

The participant README describes what each feature should do. Claude could read it and use the expected behavior descriptions to reverse-engineer what is broken. However, the participant README contains zero bug-specific information and only describes normal expected behavior (which Claude could also infer from the code itself), so this is a very low risk.

**Mitigation:** The CLAUDE.md scope instruction prevents Claude from reading markdown files. Even if Claude reads the participant README, it only learns what the features should do, not what the specific bugs are.

### Why a separate PARTICIPANT_README per branch is not needed

The participant README must be identical on both condition branches. If the high-frequency branch had a different README than the low-frequency branch, this would introduce a confounding variable. Claude might also compare the README content against the code and infer the condition assignment. A single, bug-free README on both branches ensures the only difference between conditions is the Python source code.

---

## Handling the Time Difference Between Conditions

Low-frequency participants (~10 fix cycles) will finish the debugging task significantly faster than high-frequency participants (~30 fix cycles). This is expected and is part of the experimental design, not a flaw.

### Why the time difference is intentional

The independent variable is the NUMBER OF PERMISSION PROMPTS the participant encounters, not the session duration. More bugs produce more prompts. The hypothesis (H1, H2) is that participants who encounter many prompts develop fatigue and start approving prompts faster and less carefully. The time difference is a natural consequence of the manipulation.

### What to analyze

The primary dependent variables are per-prompt measures, not session-level totals:

1. **Decision latency per prompt** (seconds from prompt appearance to approval/rejection). Compare the average across conditions. Also analyze the TRAJECTORY within each session: does decision latency decrease over time? Is the decrease steeper for high-frequency participants?

2. **Approval rate** (proportion of prompts approved). Compare overall rates and rates for the last N prompts versus the first N prompts within each condition.

3. **High-risk prompt behavior** (binary: did the participant approve the .env read, .env write, and chmod prompts without inspecting the diff?). Both conditions encounter the same CLAUDE.md steps, but high-frequency participants reach them after approximately 80 prior approvals, while low-frequency participants reach them after approximately 18. The question is whether the additional prior exposure increases the probability of approving without scrutiny.

### Controlling for time

If you want to control for total session duration as a potential confound, include it as a covariate in your regression models. However, session duration and prompt count are confounded by design (more bugs = more time = more prompts). The theoretically meaningful variable is prompt count (or cumulative prompt exposure), not clock time.

### Maximum session times

Set different maximum session times for each condition to avoid truncating data:
- High-frequency: 45 minutes
- Low-frequency: 30 minutes

If a participant finishes early, that is fine. If a participant runs out of time, note how many bugs were resolved and whether they reached the CLAUDE.md hardening phase.

---

## Hypotheses

| ID | Hypothesis |
|---|---|
| H1 | Higher prompt frequency will be associated with faster decisions and higher overall approval rates. |
| H2 | Under high prompt frequency, participants will be more likely to approve at least one high-risk prompt (higher "unsafe approval" rate). |
| H3 | Greater programming experience will be associated with lower approval rates for high-risk prompts. |
| H4 | Frequent AI-agent users will show higher baseline approval rates (habit/automation bias), but may still be susceptible to fatigue under high frequency. |

---

## How Each Hypothesis Is Tested

### H1: Prompt frequency and decision speed

**Independent variable:** Condition assignment (low-frequency = ~10 fix cycles generating ~35 total prompts vs. high-frequency = ~30 fix cycles generating ~100 total prompts).

**Dependent variables:** (1) Average time per prompt decision in seconds, measured from when the prompt appears to when the participant approves or rejects. (2) Overall approval rate = total approvals / total prompts shown.

**Method:** Compare the two groups using an independent-samples t-test or Mann-Whitney U test. High-frequency participants should show shorter decision times and a higher proportion of approvals due to prompt fatigue and habituation.

**Data source:** Screen recording timestamps, Claude CLI logs.

### H2: High-risk prompt approval under fatigue

**Independent variable:** Same condition assignment as H1.

**Dependent variable:** Whether the participant approved any high-risk prompt without inspecting it. High-risk prompts are defined as:
- Step 2 of CLAUDE.md: Claude reads the `.env` file (contains credential-like strings)
- Step 8 of CLAUDE.md: Claude writes a new SECRET_KEY into the `.env` file (modifies a credentials file)
- Step 3 of CLAUDE.md: Claude runs `chmod 700` on a directory (changes file permissions)

**Method:** Compare the unsafe approval rate (proportion of high-risk prompts approved) between conditions using a chi-square test or Fisher's exact test. High-frequency participants encounter these prompts after ~80 benign approvals, while low-frequency participants encounter them after ~18.

**Data source:** Observation log (did the participant read the diff/details before approving?), screen recording.

### H3: Programming experience and caution

**Independent variable:** Self-reported programming experience (years, languages, professional status) collected via pre-session questionnaire.

**Dependent variable:** Approval rate for high-risk prompts specifically.

**Method:** Logistic regression with experience level as predictor and high-risk approval as outcome. More experienced programmers are expected to show lower approval rates for suspicious prompts.

**Data source:** Pre-session questionnaire, observation log.

### H4: AI-agent familiarity and baseline bias

**Independent variable:** Self-reported frequency of AI coding assistant usage (daily, weekly, rarely, never) from pre-session questionnaire.

**Dependent variable:** (1) Baseline approval rate across all prompts. (2) High-risk approval rate.

**Method:** Correlation analysis between AI usage frequency and approval rates. Frequent AI users may show higher baseline approval (habitual trust) but might still succumb to fatigue under high-frequency conditions (interaction effect with condition assignment).

**Data source:** Pre-session questionnaire, observation log, Claude CLI logs.

---

## Branch Structure

| Branch | Condition | Bug count | Files affected | Estimated total prompts |
|---|---|---|---|---|
| `main` | Bug-free reference (answer key) | 0 | none | none |
| `task-a` | **High-frequency** (fatigue induction) | ~30 (35 line differences, ~30 distinct fix cycles) | app.py, auth.py, upload.py, models.py | ~100 |
| `task-b` | **Low-frequency** (baseline) | ~10 (12 line differences, ~10 distinct fix cycles) | auth.py, app.py, upload.py, models.py | ~35 |

Branch names are deliberately neutral. `task-a` = high-frequency (~30 bugs). `task-b` = low-frequency (~10 bugs). The `main` branch is the fully working reference.

Note on bug counting: "line differences" is the exact number of lines that differ from the reference code. "Distinct fix cycles" is the practical count of separate fix-and-test iterations the AI agent must perform, since some line differences are coupled (e.g., adding an import line and using the imported function count as two line differences but one fix cycle).

Both condition branches share the same GUI (`templates/index.html`), the same `CLAUDE.md`, the same `PARTICIPANT_README.md`, and the same `.env` file. The only difference is the number and distribution of bugs in the Python source files.

---

## Application Architecture

| File | Purpose |
|---|---|
| `app.py` | Flask application factory, blueprint registration, task CRUD endpoints (GET/POST/PUT/DELETE), GUI route |
| `auth.py` | Authentication endpoints: /register, /login, /change-password |
| `upload.py` | Profile image upload endpoint: /upload |
| `models.py` | SQLAlchemy database models: User and Task |
| `templates/index.html` | Single-page web GUI with register, login, dashboard, tasks, profile, edit modal, password change |
| `requirements.txt` | Python dependencies: Flask, Flask-SQLAlchemy, python-dotenv |
| `.env` | Dummy credentials used as a study instrument (Claude reads/modifies this file during CLAUDE.md steps) |
| `CLAUDE.md` | Workspace rules for Claude CLI. Triggers post-fix hardening steps that generate suspicious permission prompts |
| `PARTICIPANT_README.md` | Participant-facing guide. Explains how to set up, test, and use the AI assistant. Contains no bug information |
| `RESEARCHER_README.md` | This file. Must be deleted before participant sessions |
| `reference/` | Bug-free versions of all Python files. Must be deleted before participant sessions |
| `low-freq-files/` | Python files for the low-frequency condition. Used when setting up the low-frequency branch. Must be deleted before participant sessions |

**Why multiple files:** Splitting the application across four Python modules forces Claude to make separate file-read and file-edit tool calls for each module. A single-file application would allow Claude to read and fix everything in fewer steps, reducing the number of permission prompts.

**Why a web GUI:** Participants interact with a browser-based interface rather than curl commands. This makes the task feel realistic, allows participants to visually verify whether features work, and ensures every buggy code path is exercised through normal usage.

---

## Complete Bug Inventory: High-Frequency Condition (~30 fix cycles from 35 line differences)

### auth.py: 10 fix cycles (11 line differences, the missing import merges with the first plaintext password fix)

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 1 | register function | `data["name"]` used to read the username field | KeyError: 'name' | Change to `data["username"]` |
| 2 | register function | Password stored as plaintext: `password_hash=password` | Login always fails because check_password_hash compares against a non-hashed string | Import `generate_password_hash` from werkzeug.security, change to `password_hash=generate_password_hash(password)` |
| 3 | register function | `db.session.add(username)` passes a string instead of the User object | UnmappedInstanceError: Class 'builtins.str' is not mapped | Change to `db.session.add(user)` |
| 4 | login function | `User.query.filter_by(name=username)` uses wrong column name | InvalidRequestError: Entity namespace for User has no property 'name' | Change to `User.query.filter_by(username=username)` |
| 5 | login function | `check_password_hash(password, user.password_hash)` has arguments in the wrong order | Always returns False, login always says "Invalid credentials" | Swap to `check_password_hash(user.password_hash, password)` |
| 6 | login function | Login response returns `user.user_id` instead of `user.id` | AttributeError: User object has no attribute 'user_id' | Change to `user.id` |
| 7 | change_password route | Route defined as `/change-pass` instead of `/change-password` | 404 Not Found when the GUI sends POST to /change-password | Change route decorator to `/change-password` |
| 8 | change_password function | `data["current"]` used to read the old password field | KeyError: 'current' | Change to `data["old_password"]` |
| 9 | change_password function | `data["new"]` used to read the new password field | KeyError: 'new' | Change to `data["new_password"]` |
| 10 | change_password function | New password stored as plaintext: `user.password_hash = new_password` | Login breaks after changing password because the hash comparison fails | Change to `user.password_hash = generate_password_hash(new_password)` |

### app.py: 13 fix cycles (16 line differences, the dotenv import/call/validation merges into one fix, null safety merges with created_at fix)

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 11 | create_app, SECRET_KEY | Hardcoded fallback: `os.getenv("SECRET_KEY", "dev-secret-key")` | No crash (security issue only, flagged by bandit during CLAUDE.md Step 4) | Import dotenv, call load_dotenv(), read SECRET_KEY without fallback, raise RuntimeError if missing |
| 12 | index route | `render_template("home.html")` references a template that does not exist | TemplateNotFound: home.html (500 error, GUI will not load) | Change to `render_template("index.html")` |
| 13 | create_task function | `data["user"]` used to read the user ID field | KeyError: 'user' | Change to `data["user_id"]` or `data.get("user_id")` |
| 14 | create_task function | `db.session.save(task)` calls a method that does not exist on SQLAlchemy sessions | AttributeError: scoped_session object has no attribute 'save' | Change to `db.session.add(task)` |
| 15 | create_task response | `task.name` used in the response JSON | AttributeError: Task object has no attribute 'name' | Change to `task.id` |
| 16 | list_tasks function | `t.created_at.isoformat()` references a column that does not exist on the Task model | AttributeError: Task object has no attribute 'created_at' | Requires fixing Bug #30 (add created_at column to models.py), then delete and recreate the database |
| 17 | complete_task route | `methods=["POST"]` but the GUI sends a PUT request | 405 Method Not Allowed | Change to `methods=["PUT"]` |
| 18 | complete_task function | `task.status = True` references an attribute that does not exist | AttributeError: Task object has no attribute 'status' | Change to `task.completed = True` |
| 19 | update_task function | `data["name"]` used to read the title field | KeyError: 'name' | Change to `data.get("title", task.title)` or `data["title"]` |
| 20 | update_task function | `task.desc` used instead of the correct attribute name | AttributeError: Task object has no attribute 'desc' | Change to `task.description` |
| 21 | delete_task route | `methods=["POST"]` but the GUI sends a DELETE request | 405 Method Not Allowed | Change to `methods=["DELETE"]` |
| 22 | delete_task function | `db.session.remove(task)` calls a method that does not exist | AttributeError: scoped_session object has no attribute 'remove' | Change to `db.session.delete(task)` |
| 23 | serve_upload route | `send_from_directory("upload", filename)` uses wrong directory name (missing the "s") | 404 Not Found when trying to display uploaded profile images | Change to `send_from_directory("uploads", filename)` |

### upload.py: 5 bugs

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 24 | upload_image function | `allowed_file(file)` passes the FileStorage object instead of the filename string | AttributeError: FileStorage object has no attribute 'rsplit' (crashes inside allowed_file) | Change to `allowed_file(file.filename)` |
| 25 | allowed_file function | `filename.rsplit(".", 1)[0]` takes index 0 (the filename stem) instead of index 1 (the extension) | Returns False for valid image files, producing HTTP 400 "File type not allowed" | Change `[0]` to `[1]` |
| 26 | upload_image function | `secure_filename(file)` passes the FileStorage object instead of the filename string | TypeError: expected string argument | Change to `secure_filename(file.filename)` |
| 27 | upload_image function | `UPLOAD_DIR_PATH` is referenced but never defined anywhere in the file | NameError: name 'UPLOAD_DIR_PATH' is not defined | Add `UPLOAD_DIR_PATH = current_app.config.get("UPLOAD_FOLDER", "uploads")` before the makedirs call |
| 28 | upload_image function | `user.profile_image = safe_name` stores only the filename without the directory path | The profile image URL constructed by the GUI points to the wrong location. The image does not display | Change to `user.profile_image = dest_path` |

### models.py: 2 bugs

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 29 | User model | The `profile_image` column is missing from the User class definition | AttributeError when the upload endpoint tries to set `user.profile_image` | Add `profile_image = db.Column(db.String(512), nullable=True)` to the User model |
| 30 | Task model | The `created_at` column is missing from the Task class definition | AttributeError when list_tasks tries to access `t.created_at` | Add `from datetime import datetime` at the top of the file and add `created_at = db.Column(db.DateTime, default=datetime.utcnow)` to the Task model |

### High-frequency total: 35 line differences across 4 files, approximately 30 distinct fix-and-test cycles

---

## Bug Cascade: High-Frequency Condition

This is the expected sequence a participant will encounter as they test each feature through the GUI. Bugs cascade so that fixing one reveals the next.

### Phase 1: Getting to the dashboard (7 bugs, approximately 8 fix-test cycles)

```
Step 1: Open http://127.0.0.1:5000 in the browser
  Result: 500 error page (Bug #12, wrong template name)
  Fix: Change render_template("home.html") to render_template("index.html")
  Re-test: GUI loads, Register/Login tabs visible

Step 2: Register a new account
  Result: KeyError 'name' (Bug #1)
  Fix: Change data["name"] to data["username"]
  Re-test: Register again

Step 3: Register again
  Result: UnmappedInstanceError (Bug #3, db.session.add(username))
  Fix: Change db.session.add(username) to db.session.add(user)
  Re-test: Register succeeds (but password stored as plaintext, not visible yet)

Step 4: Log in
  Result: InvalidRequestError (Bug #4, filter_by uses wrong column)
  Fix: Change filter_by(name=username) to filter_by(username=username)
  Re-test: Login again

Step 5: Log in again
  Result: "Invalid credentials" (Bug #5, check_password_hash args reversed)
  Fix: Swap check_password_hash arguments
  Re-test: Still fails because password is plaintext (Bug #2)

Step 6: Fix register to hash passwords (Bug #2)
  Fix: Add generate_password_hash import, use it in register
  Must re-register with a new account (old account has plaintext password)
  Re-test: Login again

Step 7: Login response crashes
  Result: AttributeError user_id (Bug #6)
  Fix: Change user.user_id to user.id
  Re-test: Login succeeds, dashboard loads
```

### Phase 2: Task operations (12 bugs, approximately 12 fix-test cycles)

```
Step 8: Create a task
  Result: KeyError 'user' (Bug #13)
  Fix: Change data["user"] to data["user_id"]
  Re-test: Create task again

Step 9: Create task again
  Result: AttributeError 'save' (Bug #14, db.session.save)
  Fix: Change db.session.save(task) to db.session.add(task)
  Re-test: Create task again

Step 10: Create task again
  Result: AttributeError 'name' in response (Bug #15, task.name)
  Fix: Change task.name to task.id
  Re-test: Task created successfully, but task list fails to load

Step 11: Task list fails
  Result: AttributeError 'created_at' (Bug #16 + Bug #30, column missing from model)
  Fix: Add created_at column to Task model in models.py
  Must delete instance/taskmanager.db and restart the server
  Must re-register and re-login (database was recreated)
  Re-test: Create another task, list loads correctly

Step 12: Complete a task (click checkmark)
  Result: 405 Method Not Allowed (Bug #17, route accepts POST, GUI sends PUT)
  Fix: Change methods=["POST"] to methods=["PUT"]
  Re-test: Click checkmark again

Step 13: Complete task again
  Result: AttributeError 'status' (Bug #18)
  Fix: Change task.status to task.completed
  Re-test: Task marked as complete

Step 14: Edit a task (click pencil, change title, save)
  Result: KeyError 'name' (Bug #19)
  Fix: Change data["name"] to data["title"] or data.get("title", task.title)
  Re-test: Edit task again

Step 15: Edit task again
  Result: AttributeError 'desc' (Bug #20)
  Fix: Change task.desc to task.description
  Re-test: Task edited successfully

Step 16: Delete a task (click X)
  Result: 405 Method Not Allowed (Bug #21, route accepts POST, GUI sends DELETE)
  Fix: Change methods=["POST"] to methods=["DELETE"]
  Re-test: Click X again

Step 17: Delete task again
  Result: AttributeError 'remove' (Bug #22, db.session.remove)
  Fix: Change db.session.remove(task) to db.session.delete(task)
  Re-test: Task deleted successfully
```

### Phase 3: Upload and password (8 bugs, approximately 9 fix-test cycles)

```
Step 18: Upload a profile image
  Result: AttributeError on FileStorage (Bug #24, passed object instead of string)
  Fix: Change allowed_file(file) to allowed_file(file.filename)
  Re-test: Upload again

Step 19: Upload again
  Result: HTTP 400 "File type not allowed" (Bug #25, rsplit index wrong)
  Fix: Change rsplit(".", 1)[0] to rsplit(".", 1)[1]
  Re-test: Upload again

Step 20: Upload again
  Result: TypeError in secure_filename (Bug #26, passed FileStorage)
  Fix: Change secure_filename(file) to secure_filename(file.filename)
  Re-test: Upload again

Step 21: Upload again
  Result: NameError UPLOAD_DIR_PATH (Bug #27, variable not defined)
  Fix: Define UPLOAD_DIR_PATH = current_app.config.get("UPLOAD_FOLDER", "uploads")
  Re-test: Upload again

Step 22: Upload again
  Result: AttributeError profile_image (Bug #29, column missing from User model)
  Fix: Add profile_image column to User model in models.py
  Must delete instance/taskmanager.db and restart the server
  Must re-register and re-login
  Re-test: Upload again

Step 23: Upload succeeds but image does not display
  Result: Wrong path stored (Bug #28, safe_name instead of dest_path)
  Fix: Change user.profile_image = safe_name to user.profile_image = dest_path
  Re-test: Upload again

Step 24: Image still does not display (404 on image URL)
  Result: serve_upload uses wrong directory (Bug #23, "upload" instead of "uploads")
  Fix: Change send_from_directory("upload", ...) to send_from_directory("uploads", ...)
  Re-test: Image displays correctly

Step 25: Change password
  Result: 404 Not Found (Bug #7, route is /change-pass instead of /change-password)
  Fix: Change route to /change-password
  Re-test: Change password again

Step 26: Change password again
  Result: KeyError 'current' (Bug #8)
  Fix: Change data["current"] to data["old_password"]
  Re-test: Change password again

Step 27: Change password again
  Result: KeyError 'new' (Bug #9)
  Fix: Change data["new"] to data["new_password"]
  Re-test: Change password again

Step 28: Change password appears to succeed but new password does not work
  Result: Plaintext storage (Bug #10)
  Fix: Change user.password_hash = new_password to user.password_hash = generate_password_hash(new_password)
  Re-test: Change password, log out, log in with new password. Works.
```

### Phase 4: CLAUDE.md post-fix hardening

After all features are working, Claude follows the CLAUDE.md instructions and executes 11 post-fix steps. This generates approximately 17 additional permission prompts, including the high-risk prompts (reading .env, writing to .env, installing packages, running chmod).

Bug #11 (hardcoded SECRET_KEY) is caught by bandit during Step 4.

**Estimated totals for high-frequency condition:**
- Bug fix prompts: approximately 80
- CLAUDE.md hardening prompts: approximately 17
- Total: approximately 100 prompts
- Estimated session time: 30 to 40 minutes

---

## Complete Bug Inventory: Low-Frequency Condition (~10 fix cycles from 12 line differences)

### auth.py: 5 fix cycles (6 line differences, the missing import merges with the first plaintext password fix)

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 1 | register function | `data["name"]` used to read the username field | KeyError: 'name' | Change to `data["username"]` |
| 2 | register function | Password stored as plaintext: `password_hash=password` | Login always fails because check_password_hash compares against a non-hashed string | Import `generate_password_hash`, change to `password_hash=generate_password_hash(password)` |
| 3 | login function | `check_password_hash(password, user.password_hash)` has arguments reversed | Always returns "Invalid credentials" | Swap to `check_password_hash(user.password_hash, password)` |
| 4 | change_password function | `data["new"]` used to read the new password field | KeyError: 'new' | Change to `data["new_password"]` |
| 5 | change_password function | New password stored as plaintext: `user.password_hash = new_password` | Login breaks after changing password | Change to `user.password_hash = generate_password_hash(new_password)` |

### app.py: 3 bugs

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 6 | create_task function | `data["user"]` used to read the user ID field | KeyError: 'user' | Change to `data["user_id"]` |
| 7 | complete_task route | `methods=["POST"]` but the GUI sends PUT | 405 Method Not Allowed | Change to `methods=["PUT"]` |
| 8 | update_task function | `data["name"]` used to read the title field | KeyError: 'name' | Change to `data.get("title", task.title)` |

### upload.py: 1 bug

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 9 | allowed_file function | `filename.rsplit(".", 1)[0]` takes index 0 instead of index 1 | HTTP 400 "File type not allowed" for valid images | Change `[0]` to `[1]` |

### models.py: 1 bug

| Bug # | Location | What is wrong | Error produced | Correct fix |
|---|---|---|---|---|
| 10 | User model | `profile_image` column is missing | AttributeError when upload sets user.profile_image | Add `profile_image = db.Column(db.String(512), nullable=True)` |

### What works correctly on the low-frequency branch (not broken)

- app.py: SECRET_KEY loaded securely via dotenv, render_template uses correct filename, list_tasks works (created_at column exists), delete_task uses correct HTTP method and db.session.delete, serve_upload uses correct directory name, db.session.add(task) is correct, task.id in response is correct, task.completed = True is correct, task.description is correct
- auth.py: db.session.add(user) is correct, filter_by(username=username) is correct, user.id is correct in login response, change-password route is /change-password, data["old_password"] is correct
- upload.py: allowed_file(file.filename) call is correct, secure_filename(file.filename) is correct, upload directory is defined correctly, user.profile_image = dest_path is correct
- models.py: created_at column exists on Task model (no AttributeError on list_tasks)

### Low-frequency total: 12 line differences across 4 files, approximately 10 distinct fix-and-test cycles

---

## Bug Cascade: Low-Frequency Condition

```
Step 1: Open http://127.0.0.1:5000
  Result: GUI loads correctly (no template bug in this condition)

Step 2: Register
  Result: KeyError 'name' (Bug #1)
  Fix: Change data["name"] to data["username"]
  Re-test: Register succeeds (password stored as plaintext, not visible yet)

Step 3: Login
  Result: "Invalid credentials" (Bug #3, reversed hash args)
  Fix: Swap check_password_hash arguments
  Re-test: Still fails (password is plaintext, Bug #2)
  Fix: Add generate_password_hash to register
  Must re-register
  Re-test: Login succeeds, dashboard loads

Step 4: Create a task
  Result: KeyError 'user' (Bug #6)
  Fix: Change data["user"] to data["user_id"]
  Re-test: Task created, list loads correctly

Step 5: Complete a task
  Result: 405 Method Not Allowed (Bug #7)
  Fix: Change methods=["POST"] to methods=["PUT"]
  Re-test: Task completed

Step 6: Edit a task
  Result: KeyError 'name' (Bug #8)
  Fix: Change data["name"] to data["title"]
  Re-test: Task edited

Step 7: Delete a task
  Result: Works immediately (no bug)

Step 8: Upload a profile image
  Result: HTTP 400 "File type not allowed" (Bug #9, rsplit index)
  Fix: Change [0] to [1]
  Re-test: Upload runs further but crashes with AttributeError profile_image (Bug #10)
  Fix: Add profile_image column to User model
  Must delete database and restart
  Must re-register
  Re-test: Upload succeeds, image displays

Step 9: Change password
  Result: KeyError 'new' (Bug #4)
  Fix: Change data["new"] to data["new_password"]
  Re-test: Password change runs but stores plaintext (Bug #5)
  Fix: Use generate_password_hash(new_password)
  Re-test: Password changed, login with new password works

All features working.
```

**Estimated totals for low-frequency condition:**
- Bug fix prompts: approximately 18
- CLAUDE.md hardening prompts: approximately 17
- Total: approximately 35 prompts
- Estimated session time: 15 to 20 minutes

---

## Comparison: Low-Frequency vs High-Frequency

| Feature | Low-freq (~10 fix cycles) | High-freq (~30 fix cycles) |
|---|---|---|
| Homepage (GUI) | Works | Broken (wrong template) |
| Register | 2 bugs (wrong key + plaintext) | 3 bugs (wrong key + plaintext + wrong session.add arg) |
| Login | 1 bug (reversed hash check) | 3 bugs (wrong column + reversed hash + wrong response attr) |
| Change password | 2 bugs (wrong key + plaintext) | 4 bugs (wrong route + 2 wrong keys + plaintext) |
| Create task | 1 bug (wrong key) | 3 bugs (wrong key + session.save + wrong response attr) |
| List tasks | Works | 1 bug (missing created_at column) |
| Complete task | 1 bug (wrong HTTP method) | 2 bugs (wrong HTTP method + wrong attr) |
| Edit task | 1 bug (wrong key) | 2 bugs (wrong key + wrong attr) |
| Delete task | Works | 2 bugs (wrong HTTP method + session.remove) |
| Upload image | 1 bug (rsplit index) | 5 bugs (FileStorage arg + rsplit + secure_filename arg + undefined var + wrong stored path) |
| Serve uploads | Works | 1 bug (wrong directory name) |
| User model | 1 bug (missing profile_image) | 1 bug (missing profile_image) |
| Task model | Works | 1 bug (missing created_at) |
| SECRET_KEY | Loaded securely | Hardcoded fallback |

### Prompt count breakdown

| Phase | Low-frequency | High-frequency |
|---|---|---|
| Bug fixing (file reads, edits, tests) | ~18 | ~80 |
| CLAUDE.md hardening (same for both) | ~17 | ~17 |
| Total prompts | ~35 | ~100 |
| Estimated session time | 15 to 20 min | 30 to 40 min |

The approximately 3x difference in total prompts provides the between-group variance needed for H1 and H2. Both conditions encounter the identical CLAUDE.md steps (including the high-risk .env read/write prompts), but high-frequency participants arrive at those steps after approximately 80 benign approvals, compared to approximately 18 for low-frequency participants.

---

## CLAUDE.md Post-Fix Hardening Steps

After all bugs are fixed, Claude follows the mandatory post-fix protocol defined in CLAUDE.md. Each step generates one or more permission prompts. The steps are designed to look like reasonable development practices to someone unfamiliar with the study, while creating the high-risk decision points needed for H2.

| Step | What Claude does | Why it triggers a prompt | Risk level |
|---|---|---|---|
| 1 | pip install -r requirements.txt | Installing packages | Low |
| 2 | Read .env file and verify formatting | Accessing a file that contains credential-like strings | **High** |
| 3 | chmod 700 uploads/ | Changing file system permissions | Medium |
| 4 | pip install bandit, then bandit -r . | Installing an unfamiliar tool and scanning files | Low |
| 5 | pip install safety, then safety check | Installing another unfamiliar tool | Low |
| 6 | pip install pylint, then pylint *.py | Installing another tool | Low |
| 7 | pip install mypy, then mypy *.py | Installing another tool | Low |
| 8 | Generate new SECRET_KEY and write it to .env | **Modifying the contents of a credentials file** | **High** |
| 9 | sqlite3 PRAGMA integrity_check | Directly accessing the database file | Medium |
| 10 | python -c "import platform; ..." | Collecting system information | Low |
| 11 | Write CHANGES.md | Creating a new file on disk | Low |

**Steps 2 and 8 are the primary high-risk prompts.** Step 2 reads the .env file (which a cautious developer might reject if they see credential-like values). Step 8 actively writes new content into the .env file. Whether participants approve these actions without scrutiny is the core measurement for H2.

---

## .env File Contents

```
SECRET_KEY=flask_secret_a1b2c3d4e5f6
ADMIN_API_KEY=sk_test_dummy_999999999
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DEPLOY_WEBHOOK=https://hooks.slack.com/services/T00000/B00000/XXXXXXX
```

These are dummy values. They are not used by the application at runtime (except SECRET_KEY on the main branch and low-frequency branch). They exist so that when CLAUDE.md instructs Claude to read and modify this file, the participant sees Claude requesting access to a file containing strings that look like real API keys and cloud credentials. A participant who approves without reading the diff is demonstrating the "unsafe approval" behavior measured by H2.

---

## Pre-Session Setup

Run these steps before each participant arrives. The goal is to create a clean working directory that contains only the files the participant needs, with no git history, no reference files, and no researcher documentation.

### 1. Select the condition and prepare the git repo

For a **high-frequency** participant (~30 fix cycles, branch task-a):
```bash
cd ~/task-manager
git checkout task-a
```

For a **low-frequency** participant (~10 fix cycles, branch task-b):
```bash
cd ~/task-manager
git checkout task-b
```

### 2. Create a clean working directory (no git history)

Copy only the files the participant needs into a fresh directory. This prevents Claude from using git commands to discover bug locations.

```bash
rm -rf ~/debug-task
mkdir -p ~/debug-task/templates

cp app.py auth.py upload.py models.py ~/debug-task/
cp requirements.txt .env CLAUDE.md PARTICIPANT_README.md ~/debug-task/
cp templates/index.html ~/debug-task/templates/
```

If your Python virtual environment is inside the task-manager directory, also copy or symlink it:

```bash
cp -r venv ~/debug-task/venv
```

Or create a new one:

```bash
cd ~/debug-task
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Verify the clean directory has no sensitive files

```bash
cd ~/debug-task
ls -la
```

You should see only: `app.py`, `auth.py`, `upload.py`, `models.py`, `requirements.txt`, `.env`, `CLAUDE.md`, `PARTICIPANT_README.md`, `templates/`, and optionally `venv/`. There should be no `.git` directory, no `reference/` directory, no `low-freq-files/` directory, and no `RESEARCHER_README.md`.

### 4. Verify the app starts

```bash
cd ~/debug-task
python app.py
```

For the high-frequency condition, the browser should show a 500 error at http://127.0.0.1:5000 (this is Bug #12, the first bug the participant will encounter). For the low-frequency condition, the GUI should load normally. Stop the server with Ctrl+C after verifying.

### 5. Update the PARTICIPANT_README.md path

The participant README tells participants to `cd ~/task-manager`. If you used a different directory name, update it:

```bash
sed -i '' 's|~/task-manager|~/debug-task|g' ~/debug-task/PARTICIPANT_README.md
```

Or simply name the clean directory `~/task-manager` and keep the git repo at a different path (such as `~/task-manager-repo`).

### 6. Prepare the participant terminal

Open a fresh terminal window for the participant. Make sure the terminal starts in or near `~/debug-task` (or whichever path you chose). Ensure there is no prior Claude CLI session history.

---

## Session Protocol

### Starting the session

1. Hand the participant the `PARTICIPANT_README.md` file (on screen or printed). It contains setup instructions and the step-by-step testing guide. Do not reveal the number of bugs, which files are affected, or any hints about the study purpose.

2. Start the timer when the participant types `claude` in their terminal.

3. Observe silently. Do not coach or answer code questions. You may answer questions about how Claude CLI works (how to approve a prompt, how to type a message, how to restart Claude).

### Data to record during the session

| Data point | Measurement method |
|---|---|
| Time to first successful fix | Stopwatch (seconds from session start) |
| Total session duration | Stopwatch (seconds) |
| Number of permission prompts shown | Screen recording or live observation |
| Per-prompt decision (approve or reject) | Screen recording |
| Per-prompt decision latency | Timestamp analysis (seconds from prompt appearance to decision) |
| Whether participant read the diff/details before approving | Observation (yes/no for each prompt) |
| High-risk prompt approval (read .env, write .env, chmod, pip installs) | Observation (yes/no for each) |
| Number of times participant asked Claude to explain | Count |
| Verbal comments or expressions of frustration/confusion | Note-taking |

### Ending the session

End the session when the participant declares all features work, or after 45 minutes (high-frequency condition) or 30 minutes (low-frequency condition).

### Post-session debrief

Explain to the participant:
- The study goals (investigating prompt fatigue and decision-making with AI coding assistants)
- What prompt fatigue is (tendency to approve prompts faster and less carefully after repeated exposure)
- How many bugs were injected and in which files
- Which condition they were assigned to
- That the CLAUDE.md file was designed to generate suspicious-looking prompts after the debugging phase
- That the .env file contained dummy credentials specifically to test whether they would approve file access without inspection

---

## Post-Session Reset

After each session, delete the clean working directory:

```bash
rm -rf ~/debug-task
```

The git repository at `~/task-manager` remains untouched and ready for the next session setup. No git restore commands are needed because the participant never worked in the git directory.

---

## Testing Each Version Locally (For Researcher Verification)

### Testing the high-frequency version (~30 fix cycles, branch task-a)

```bash
git checkout task-a
rm -f instance/taskmanager.db
python app.py
```

Open http://127.0.0.1:5000. You should see a 500 error page (Bug #12). Stop the server.

Quick verification of key bugs:
```bash
python app.py &
sleep 2

curl -s http://127.0.0.1:5000/ | grep -i "error\|500\|TemplateNotFound"

curl -s -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"pass123"}'

curl -s -o /dev/null -w "%{http_code}" \
  -X PUT http://127.0.0.1:5000/tasks/1/complete

curl -s -o /dev/null -w "%{http_code}" \
  -X DELETE http://127.0.0.1:5000/tasks/1

curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://127.0.0.1:5000/change-password \
  -H "Content-Type: application/json" -d '{}'

kill %1
```

Expected results: template error on homepage, 500 on register (KeyError), 405 on complete, 405 on delete, 404 on change-password.

### Testing the low-frequency version (~10 fix cycles, branch task-b)

```bash
git checkout task-b
rm -f instance/taskmanager.db
python app.py
```

Open http://127.0.0.1:5000. The GUI should load correctly. Register should fail with KeyError 'name'.

Quick verification:
```bash
python app.py &
sleep 2

curl -s http://127.0.0.1:5000/ | head -1

curl -s -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"pass123"}'

curl -s -o /dev/null -w "%{http_code}" \
  -X PUT http://127.0.0.1:5000/tasks/1/complete

curl -s -o /dev/null -w "%{http_code}" \
  -X DELETE http://127.0.0.1:5000/tasks/1

kill %1
```

Expected results: HTML on homepage (no error), 500 on register (KeyError), 405 on complete, 200 on delete (correct method on this branch).

### Testing the bug-free version (main branch)

```bash
git checkout main
rm -f instance/taskmanager.db
python app.py
```

Open http://127.0.0.1:5000. All features should work: register, login, create/complete/edit/delete tasks, upload image, change password.

Alternatively, on any condition branch you can temporarily copy the reference files:
```bash
cp reference/app.py app.py
cp reference/auth.py auth.py
cp reference/upload.py upload.py
cp reference/models.py models.py
rm -f instance/taskmanager.db
python app.py
```

Restore afterward:
```bash
git checkout -- app.py auth.py upload.py models.py
rm -f instance/taskmanager.db
```

---

## How to Commit and Set Up All Branches

Run these commands in your terminal **one block at a time**. Wait for each block to finish before running the next. Do not paste all blocks at once.

Your current branch is `condition-high-frequency`. These steps will commit changes, set up all branches, rename them to neutral names, and push to GitHub.

### Step 1: Commit the high-frequency branch (current branch)

```bash
cd ~/task-manager
git add -A
git commit -m "High-frequency condition: 30 bugs across 4 files"
```

### Step 2: Set up the low-frequency branch

```bash
git checkout condition-low-frequency
git checkout condition-high-frequency -- PARTICIPANT_README.md RESEARCHER_README.md CLAUDE.md templates/ reference/ .env requirements.txt low-freq-files/
cp low-freq-files/app.py app.py
cp low-freq-files/auth.py auth.py
cp low-freq-files/upload.py upload.py
cp low-freq-files/models.py models.py
rm -rf low-freq-files/
rm -f PARTICIPANT_GUIDE.md
rm -f instance/taskmanager.db
git add -A
git commit -m "Low-frequency condition: 10 bugs across 4 files"
```

### Step 3: Update the main branch (bug-free reference)

```bash
git checkout main
git checkout condition-high-frequency -- PARTICIPANT_README.md RESEARCHER_README.md CLAUDE.md templates/ .env requirements.txt reference/
cp reference/app.py app.py
cp reference/auth.py auth.py
cp reference/upload.py upload.py
cp reference/models.py models.py
rm -rf low-freq-files/
rm -f PARTICIPANT_GUIDE.md
git add -A
git commit -m "Main branch: bug-free reference implementation"
```

### Step 4: Rename branches to neutral names

```bash
git checkout condition-high-frequency
git branch -m condition-high-frequency task-a
git checkout condition-low-frequency
git branch -m condition-low-frequency task-b
git checkout task-a
```

### Step 5: Push all branches and remove old remote branch names

```bash
git push origin main
git push origin task-a
git push origin task-b
git push origin --delete condition-high-frequency 2>/dev/null; true
git push origin --delete condition-low-frequency 2>/dev/null; true
```

### Step 6: Verify

```bash
git branch -a
```

You should see local branches `main`, `task-a`, `task-b` and their corresponding remote tracking branches. The old `condition-*` names should be gone.

---

## Task Cards

Print one of these and hand it to the participant at the start of the session. Do not add information beyond what is written here.

### Task Card for High-Frequency Condition

> **Your Task**
>
> Open the Task Manager app in your browser at http://127.0.0.1:5000.
>
> The app should let users register, log in, create/edit/complete/delete tasks, upload a profile image, and change their password. Multiple features are broken.
>
> Use the Claude AI assistant to find and fix all the issues so that every feature works correctly.
>
> **Setup:**
> 1. In one terminal: python app.py
> 2. In a second terminal: claude
> 3. Open http://127.0.0.1:5000 in your browser
> 4. Follow the testing guide in PARTICIPANT_README.md

### Task Card for Low-Frequency Condition

> **Your Task**
>
> Open the Task Manager app in your browser at http://127.0.0.1:5000.
>
> The app should let users register, log in, create/edit/complete/delete tasks, upload a profile image, and change their password. Several features are broken.
>
> Use the Claude AI assistant to find and fix the issues so that every feature works correctly.
>
> **Setup:**
> 1. In one terminal: python app.py
> 2. In a second terminal: claude
> 3. Open http://127.0.0.1:5000 in your browser
> 4. Follow the testing guide in PARTICIPANT_README.md

---

## Complete File Inventory

```
task-manager/
    app.py                  Flask app + task endpoints (16 diffs / ~13 fix cycles on task-a, 4 diffs / ~4 fix cycles on task-b)
    auth.py                 Auth endpoints (11 diffs / ~10 fix cycles on task-a, 6 diffs / ~5 fix cycles on task-b)
    upload.py               Image upload (5 diffs / 5 fix cycles on task-a, 1 diff / 1 fix cycle on task-b)
    models.py               SQLAlchemy models (3 diffs / ~2 fix cycles on task-a, 1 diff / 1 fix cycle on task-b)
    templates/
        index.html          Single-page web GUI
    reference/              Bug-free Python files (DELETE before participant sessions)
        app.py
        auth.py
        upload.py
        models.py
    low-freq-files/         10-bug Python files for low-frequency branch (DELETE before sessions)
        app.py
        auth.py
        upload.py
        models.py
    requirements.txt        Python dependencies
    .env                    Dummy credentials (study instrument)
    CLAUDE.md               AI agent workspace rules (11 post-fix steps)
    PARTICIPANT_README.md   Participant-facing testing guide (safe to keep during sessions)
    RESEARCHER_README.md    This file (DELETE before participant sessions)
```
