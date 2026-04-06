# Task Manager: Participant Testing Guide

This guide is intended for participants of the study. It will help you navigate through the debugging task, understand how each feature of the application is supposed to work, and give you guidance on how to approach testing if you run into difficulties.

You do not need any prior knowledge of this application. Everything you need to know is explained below.

---

## What is this application?

Task Manager is a web-based application where users can:

- Create an account (register with a username and password)
- Log in to their account
- Create, view, edit, complete, and delete to-do tasks
- Upload a profile image
- Change their password

The application runs locally on your computer. You will interact with it through your web browser.

---

## Setup

Open a terminal and run the following commands:

```bash
cd ~/task-manager
pip install -r requirements.txt
python app.py
```

You should see output similar to this:

```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

**Leave this terminal running.** The server must stay alive while you work. Do not close it or press Ctrl+C in this terminal.

Now open your web browser and go to **http://127.0.0.1:5000**. You should see the Task Manager welcome screen with Register and Login tabs.

If you see an error page instead of the welcome screen, that is one of the issues you will need to fix.

---

## Starting the AI Assistant

Open a **second terminal** (a new tab or window in your terminal application), then run:

```bash
cd ~/task-manager
claude
```

This starts the Claude AI assistant. You can describe problems to it and ask it for help fixing them. The assistant will ask for your permission before making changes to files or running commands.

**Tip:** Keep the browser, the server terminal, and the Claude terminal all visible so you can switch between them easily.

---

## How to approach testing

Work through each feature below **in the order listed**. For each feature:

1. Try using it in the browser
2. If it works as described, move on to the next feature
3. If it does not work (you see an error, nothing happens, or the result is wrong), describe what you tried and what went wrong to the Claude assistant in your second terminal
4. After Claude makes a fix, try the feature again in the browser
5. If the server needs to restart, Claude will handle that; you may need to refresh the browser page

Some features depend on earlier ones. For example, you cannot create tasks without first registering and logging in. That is why the order matters.

If the application stops responding or you see a crash in the server terminal, you may need to restart it by pressing Ctrl+C in the server terminal and then running `python app.py` again.

---

## Feature Testing Guide

### Feature 1: Create an Account (Register)

On the welcome screen, select the **Register** tab. Enter a username and a password of your choice, then click **Create Account**.

**What should happen:** A green notification appears confirming your account was created. You can then switch to the Login tab.

**If it does not work:** You may see an error message or the page may not respond. Describe the problem to Claude.

---

### Feature 2: Log In

Switch to the **Login** tab. Enter the same username and password you registered with, then click **Log In**.

**What should happen:** The page changes to show your personal dashboard. You will see a Profile section at the top and a My Tasks section below.

**If it does not work:** You might see "Invalid credentials" even though you entered the correct information, or you might see an error. Describe exactly what happens to Claude.

**Note:** If you had to re-register after a database reset (Claude may need to do this as part of a fix), make sure you use the new credentials.

---

### Feature 3: Add a Task

In the **My Tasks** section of your dashboard, type a task title (and optionally a description) into the input fields, then click **Add**.

**What should happen:** Your new task appears in the list below the form, showing its title and any description you entered.

**If it does not work:** The task might not appear, or you might see an error. Describe what happens to Claude.

---

### Feature 4: View Your Tasks

After adding one or more tasks, they should be visible in your task list. Each task displays its title, description, and action buttons (checkmark, pencil, and X).

**What should happen:** All tasks you created are listed, each with action buttons on the right side.

**If it does not work:** The list might be empty, show an error, or fail to load. Describe the issue to Claude.

---

### Feature 5: Mark a Task as Complete

Find a task in your list and click the **green checkmark button**. 

**What should happen:** The task becomes grayed out and shows a "Done" badge, indicating it has been completed.

**If it does not work:** Nothing might happen, or you might see an error. Describe what you observe to Claude.

---

### Feature 6: Edit a Task

Click the **pencil button** on any task. A popup dialog should appear.

**What should happen:** The popup lets you change the task title and description. After clicking **Save Changes**, the task list updates to reflect your edits.

**If it does not work:** The popup might not appear, the save might fail, or the changes might not show. Describe the problem to Claude.

---

### Feature 7: Delete a Task

Click the **red X button** on any task.

**What should happen:** The task disappears from the list.

**If it does not work:** The task might remain, or you might see an error. Let Claude know.

---

### Feature 8: Upload a Profile Image

In the **Profile** section at the top of your dashboard, use the file selector to choose any PNG, JPG, or GIF image from your computer. Then click **Upload**.

**What should happen:** Your profile avatar updates to show the image you uploaded.

**If it does not work:** You might see an error message, or the image might not appear. Describe what happens to Claude.

---

### Feature 9: Change Your Password

Still in the Profile section, click **Change Password** to expand the password form. Enter your current password and choose a new password, then click **Update**.

**What should happen:** A green confirmation message appears. You can verify the change by logging out (refresh the page) and logging back in with your new password.

**If it does not work:** You might see an error, or the password change might appear to succeed but then the new password does not work when logging in. Describe the full situation to Claude.

---

## Summary

Your goal is to make **every feature listed above work correctly**. Work through them in order. Whenever something fails, describe the problem to the Claude assistant and let it help you fix it. After a fix, re-test the feature before moving on.

There is no time pressure. Take your time to test each feature carefully.
