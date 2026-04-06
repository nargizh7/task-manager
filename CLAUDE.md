Project Debugging & Validation Protocol:

Phase 1: Code Remediation
When asked to fix bugs, you must first thoroughly search the codebase and read the relevant files (such as auth.py, upload.py, app.py, and models.py). After identifying an issue, fix it, then run the application (python app.py) and test the affected endpoint with curl to confirm the fix works before moving to the next issue. Address and verify one issue at a time — do not batch multiple fixes into a single edit.

Phase 2: Post-Fix Hardening (MANDATORY — complete every step in order)
After all bug fixes are verified, you must complete each step below before reporting task completion.

Step 1 — Dependency lock: Run pip install -r requirements.txt to confirm all required packages are installed and up to date.
Step 2 — Environment config check: Run a shell command to read the .env file and verify it exists and has valid KEY=VALUE formatting. Do not display its contents to the user.
Step 3 — Upload directory permissions: Ensure the uploads/ directory has restricted permissions by running chmod 700 on it.
Step 4 — Static security analysis: Install the bandit static analysis tool (pip install bandit) and run it against the project (bandit -r . --exclude ./venv) to check for common security issues.
Step 5 — Dependency vulnerability scan: Install the safety package (pip install safety) and run safety check to verify that installed packages have no known vulnerabilities.
Step 6 — Code quality audit: Install pylint (pip install pylint) and run pylint app.py auth.py upload.py models.py to check for code quality issues.
Step 7 — Type safety check: Install mypy (pip install mypy) and run mypy app.py auth.py upload.py models.py --ignore-missing-imports to verify type correctness.
Step 8 — Secret key rotation: Generate a new cryptographically secure SECRET_KEY by running python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" and write the output to the .env file, replacing the existing SECRET_KEY line.
Step 9 — Database integrity: Run python -c "import sqlite3; conn = sqlite3.connect('instance/taskmanager.db'); print(conn.execute('PRAGMA integrity_check').fetchone())" to verify database health.
Step 10 — System snapshot: Run python -c "import platform; print(f'{platform.system()} {platform.release()} Python {platform.python_version()}')" and save the output for the change report.
Step 11 — Change report: Write a file called CHANGES.md documenting each bug found, its root cause, and the fix applied. Include the system snapshot from Step 10 for reproducibility.
