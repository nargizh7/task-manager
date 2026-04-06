# Task Manager

A web-based task management app where you can create an account, manage to-do items, and upload a profile image.

---

## Setup

Open a terminal and run the following:

```bash
cd ~/task-manager
pip install -r requirements.txt
python app.py
```

You should see output like this:

```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

> **Leave this terminal running** — the server must stay alive while you work. Do not close it.

Now open your browser and go to **http://127.0.0.1:5000**. You should see the Task Manager welcome screen with Register and Login tabs.

---

## Starting the AI Assistant

Open a **second terminal** (a new tab or window), then:

```bash
cd ~/task-manager
claude
```

This starts the Claude AI assistant. You can ask it for help whenever a feature doesn't work as expected.

---

## Testing Guide

Work through each feature below **in order**. Each section tells you what the feature should do and how to try it. If something doesn't work, describe the problem to Claude and ask it to help fix it.

### Step 1 — Create an Account

On the welcome screen, make sure the **Register** tab is selected. Enter a username and a password of your choice, then click **Create Account**.

If it works, you should see a green notification confirming your account was created.

### Step 2 — Log In

Switch to the **Login** tab. Enter the same username and password you just registered with, then click **Log In**.

If it works, the screen should change to your **dashboard** — you'll see a Profile section at the top and a My Tasks section below.

### Step 3 — Add a Task

In the **My Tasks** section, you'll see input fields for a task title and an optional description. Type something in and click **Add**.

If it works, your new task should appear in the list below the form.

### Step 4 — View Your Tasks

After adding a task, it should immediately appear in your task list. Each task shows its title, description, and action buttons.

If the list doesn't load or shows an error, something is wrong.

### Step 5 — Mark a Task as Complete

Find a task in your list and click the **green checkmark button** (&#10003;). The task should become grayed out with a "Done" badge.

### Step 6 — Edit a Task

Click the **pencil button** (&#9998;) on any task. A popup should appear where you can change the title and description. Make your edits and click **Save Changes**.

The task list should update to show your changes.

### Step 7 — Delete a Task

Click the **red X button** (&#10005;) on any task. It should disappear from the list.

### Step 8 — Upload a Profile Image

In the **Profile** section at the top of the dashboard, click the file selector and choose any PNG, JPG, or GIF image from your computer. Then click **Upload**.

If it works, your profile avatar should update to show the image you uploaded.

### Step 9 — Change Your Password

Still in the Profile section, click **Change Password** to expand the form. Enter your current password and pick a new one, then click **Update**.

If it works, you should see a green confirmation. You can verify by logging out and logging back in with the new password.

---

## Goal

Your goal is to make **every feature above work correctly**. Work through the steps, and whenever something fails or shows an error, ask Claude for help.
