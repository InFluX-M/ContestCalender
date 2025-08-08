import requests
from lxml import html
from datetime import datetime
from zoneinfo import ZoneInfo
import re

class AtcoderContestManager():
    def __init__(self):
        self.contests = []
        self.url = "https://atcoder.jp/contests/"
        self.add_contests()

    def extract_name(self, raw_str):
        cleaned = raw_str.strip()
        cleaned = re.sub(r'^[^\w(]+', '', cleaned)  # strip icons at start but keep ( )
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def to_tehran_time(self, dt_str):
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")
        tehran_time = dt.astimezone(ZoneInfo("Asia/Tehran"))
        return tehran_time

    def to_minutes(self, time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def is_target_contest(self, name):
        name_lower = name.lower()
        return (
            "atcoder beginner contest" in name_lower
            or ("atcoder regular contest" in name_lower and "div. 2" in name_lower)
        )

    def add_contests(self):
        response = requests.get(self.url)
        tree = html.fromstring(response.content)
        trs = tree.xpath('//*[@id="contest-table-upcoming"]/div/div/table/tbody/tr')

        print(f"Found {len(trs)} rows")
        for tr in trs:
            tds = tr.xpath("./td")

            # --- Date ---
            date_str = tds[0].text_content().strip()
            tehran_time = self.to_tehran_time(date_str)
            print(f"Tehran time: {tehran_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # --- Contest name & URL ---
            link_elem = tds[1].xpath("./a")[0]  # the <a> tag inside the second <td>
            href = link_elem.get("href").strip()
            name = self.extract_name(link_elem.text_content())
            print(f"Contest name: {name}")
            print(f"URL: {href}")

            # --- Length in minutes ---
            length_str = tds[2].text_content().strip()
            minutes = self.to_minutes(length_str)
            print(f"Length in minutes: {minutes}")

            # --- Filter target contests ---
            if self.is_target_contest(name):
                contest = {
                    "name": name,
                    "start_time": tehran_time,
                    "length": minutes,
                    "url": href if href.startswith("http") else f"https://atcoder.jp{href}"
                }
                self.contests.append(contest)
                print(f"Added contest: {contest['name']} at {contest['start_time']} with length {contest['length']} minutes")

class CFContestManager:
    def __init__(self):
        self.contests = []
        self.url = "https://codeforces.com/api/contest.list?gym=false"
        self.tehran_tz = ZoneInfo("Asia/Tehran")
        self.add_contests()

    def is_target_contest(self, name):
        name_lower = name.lower()
        return (
            "div. 2" in name_lower
            or "div. 3" in name_lower
            or "div. 4" in name_lower
        )

    def add_contests(self):
        response = requests.get(self.url)
        data = response.json()

        if data['status'] != 'OK':
            print("Failed to fetch contests")
            return

        for contest in data['result']:
            if contest['phase'] == "BEFORE" and self.is_target_contest(contest['name']):
                # startTimeSeconds is UTC timestamp
                start_time_utc = datetime.fromtimestamp(contest['startTimeSeconds'], tz=ZoneInfo("UTC"))
                start_time_tehran = start_time_utc.astimezone(self.tehran_tz)

                contest_info = {
                    'name': contest['name'],
                    'start_time': start_time_tehran,
                    'length': contest['durationSeconds'] // 60,
                    'url': f"https://codeforces.com/contest/{contest['id']}"
                }
                self.contests.append(contest_info)
                print(f"Added contest: {contest_info['name']} at {contest_info['start_time'].strftime('%Y-%m-%d %H:%M:%S %Z%z')} with length {contest_info['length']} minutes")
