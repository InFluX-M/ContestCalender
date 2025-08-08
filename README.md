# Contest Calendar Syncer

This project fetches upcoming programming contests from **Atcoder** and **Codeforces** and automatically adds them as events to your Google Calendar. It avoids adding duplicate contests and sets reminders for each contest.

---

## Features

- Scrapes upcoming contests from Atcoder and Codeforces APIs/pages.
- Filters contests based on contest types (e.g., Div.2, Div.3, Atcoder Beginner Contests).
- Converts contest start times to Tehran timezone.
- Adds contests within the next 7 days to Google Calendar.
- Avoids duplicates by checking existing calendar events.
- Adds email and popup reminders for each contest.
- Uses Google Calendar API with OAuth2 authentication.

---

## Prerequisites

- Python 3.9+
- Google Cloud Project with Calendar API enabled
- `cred.json` Google OAuth client secrets file (download from Google Cloud Console)
- Required Python packages:
  - `requests`
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-api-python-client`
  - `lxml`

---

## Installation

1. Clone this repository in home:
   ```bash
   git clone https://github.com/yourusername/contest-calendar-syncer.git
   cd contest-calendar-syncer
   ```
   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
3. Download your Google API credentials JSON from Google Cloud Console and save it as cred.json in the project root.

---

## Usage
Run the main script to fetch contests and add them to your Google Calendar:

   ```bash
   python calender.py
   ```


- On first run, a browser window will open to authorize the app with your Google account.
- OAuth tokens are saved to token.json for subsequent runs.
- Contests within the next 7 days will be added with reminders.
- Duplicate contests already in your calendar will be skipped.

---

## Customization

- Modify contest filtering logic inside AtcoderContestManager.is_target_contest() and CFContestManager.is_target_contest() to include other contests if desired.
- Change the reminder times or add/remove attendees in the event creation part of main.py.
- Adjust the timezone by modifying the timezone strings (Asia/Tehran) if you want a different local time.

---

## Files Overview

- main.py — The main entry point that authenticates and inserts contests into Google Calendar.
- contest.py — Contains AtcoderContestManager and CFContestManager classes for fetching and parsing contest data.
- cred.json — Your Google API client secrets (not included in repo, you provide this).
- token.json — Stores OAuth tokens after authorization (auto-generated).

---

## Notes

- Make sure your Google Calendar API is enabled and you have created OAuth credentials.
- The script uses the primary calendar by default.
- The timezone is set to Tehran (Asia/Tehran) throughout for consistency with Atcoder and Codeforces contest times.

---


