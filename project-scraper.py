import httpx
import json
from datetime import datetime
from pathlib import Path

KB_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34.json?page={}"

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.7",
    "cache-control": "no-cache",
    "discourse-logged-in": "true",
    "discourse-present": "true",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34",
    "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "x-csrf-token": "lfVoblER3Q-UFISIP4kmRYo7GPhG8kGl8-lwk4b2l31G_NiD6LmBS0Mkjv2P8yPvp5LvDxHrob-NapPwb_J_cA",
    "x-requested-with": "XMLHttpRequest",
}

cookies = json.loads(Path("./cookies.json").read_text())

start_date = datetime.fromisoformat("2025-01-01")
end_date = datetime.fromisoformat("2025-04-14")
links = []

for i in range(1, 100):  # soft limit, don't hammer the server too much
    c = KB_URL.format(i)
    resp = httpx.get(c, headers=headers, cookies=cookies).json()
    added_this_round = 0
    for topic in resp["topic_list"]["topics"]:
        created_at = datetime.fromisoformat(
            topic["created_at"][:10]
        )  # limit to ISO date Y-m-d
        if not (start_date <= created_at <= end_date):
            continue
        slug = topic["slug"]
        id = topic["id"]
        url = f"{slug}/{id}.json"
        links.append(url)
        added_this_round += 1

    # we are way back in the past, pack up
    if len(links) != 0 and added_this_round == 0:
        break

POST_BASE = "https://discourse.onlinedegree.iitm.ac.in/t/{}"

for link in links:
    url = POST_BASE.format(link)
    resp = httpx.get(url, headers=headers, cookies=cookies)
    out_path = link.replace("/", "-")
    (Path("discourse-posts") / out_path).write_text(resp.text)

print(links)
