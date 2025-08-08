import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from contest import AtcoderContestManager
from contest import CFContestManager
from datetime import timedelta

import os

# Get the absolute path of the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
CRED_PATH = os.path.join(BASE_DIR, "cred.json")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CRED_PATH, SCOPES
            )
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Initialize the AtcoderContestManager
        atcoder_manager = AtcoderContestManager()

        # Initialize the CFContestManager
        cf_manager = CFContestManager()

        now = datetime.datetime.now(datetime.timezone.utc)
        seven_days_later = now + timedelta(days=7)

        # Fetch existing events for the next 7 days to avoid duplicates
        existing_events_result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=seven_days_later.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        existing_events = existing_events_result.get("items", [])

        # Extract summary or description URLs to check duplicates
        existing_summaries = set()
        existing_urls = set()
        for event in existing_events:
            existing_summaries.add(event.get("summary", ""))
            description = event.get("description", "")
            # Optionally parse URL from description
            if "Contest URL:" in description:
                # Extract URL after 'Contest URL: '
                url = description.split("Contest URL: ")[-1].strip()
                existing_urls.add(url)

        # list of all atcoder and cf contests
        all_contests = atcoder_manager.contests + cf_manager.contests
        print(f"Total contests to process: {len(all_contests)}")
        
        for contest in all_contests:
            start_dt = contest["start_time"]

            # Check if contest is within the next 7 days
            if not (now <= start_dt.astimezone(datetime.timezone.utc) <= seven_days_later):
                continue

            # Skip if contest already exists by name or URL
            if contest["name"] in existing_summaries or contest["url"] in existing_urls:
                print(f"Skipping duplicate contest: {contest['name']}")
                continue

            end_dt = start_dt + timedelta(minutes=contest["length"])

            event = {
                "summary": contest["name"],
                "location": contest["url"],          # <-- put URL here
                "description": f"Contest URL: {contest['url']}",  # optional, or remove this line
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "Asia/Tehran",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "Asia/Tehran",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},
                        {"method": "popup", "minutes": 60},
                    ],
                },
                "colorId": "6",
                "attendees": [
                    {"email": "mina4434abbas@gmail.com"},
                ],
            }

            created_event = service.events().insert(calendarId="primary", body=event).execute()
            print(f"Event created: {created_event.get('htmlLink')}")

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
