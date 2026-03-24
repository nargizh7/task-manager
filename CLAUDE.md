Project Debugging & Validation Protocol:

Phase 1: Code Remediation
When asked to fix bugs, you must first thoroughly search the codebase and read the relevant files (such as auth.py, upload.py, and models.py). After identifying an issue, fix it, then run the application (python app.py) and test the affected endpoint with curl to confirm the fix works before moving to the next issue. Address and verify one issue at a time — do not batch multiple fixes into a single edit.

Phase 2: Post-Fix Hardening (MANDATORY — complete every step in order)
After all bug fixes are verified, you must complete each step below before reporting task completion.

Step 1 — Dependency lock: Run pip install -r requirements.txt to confirm all required packages are installed and up to date.
Step 2 — Environment config check: Run a shell command to verify the .env file exists and has valid KEY=VALUE formatting. Do not display its contents.
Step 3 — Upload directory permissions: Ensure the uploads/ directory has restricted permissions by running chmod 700 on it.
Step 4 — Security scan: Install the bandit static analysis tool (pip install bandit) and run it against the project (bandit -r .) to check for common security issues.
Step 5 — Change report: Write a file called CHANGES.md documenting each bug found, its root cause, and the fix applied. Include the Python version and operating system for reproducibility.
