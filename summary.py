import csv
import os
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()
BASE_LINK = os.environ["JIRA_BASE"]
AUTH = (os.environ["JIRA_EMAIL"], os.environ["JIRA_TOKEN"])

JQL_QUERY = "project = ACT ORDER BY created DESC"
CUSTOM_FIELDS = [ "Ajuntament", "Canal d'entrada" ]

def fields_ids(names):
    req = requests.get(f"{BASE_LINK}/rest/api/3/field", auth=AUTH)
    req.raise_for_status()
    per_name = { f["name"]: f["id"] for f in req.json() }
    missing = [ n for n in names if n not in per_name ]
    if missing:
        raise SystemExit(f"Custom fields not found in Jira: {missing}")
    return { n: per_name[n] for n in names }

def search(jql, fields):
    token = None
    while True:
        params = { "jql": jql, "fields": ",".join(fields), "maxResults": 100 }
        if token:
            params["nextPageToken"] = token
        req = requests.get(
            f"{BASE_LINK}/rest/api/3/search/jql",
            params=params,
            auth=AUTH,
            headers={"Accept": "application/json"}
        )
        req.raise_for_status()
        data = req.json()
        yield from data["issues"]
        token = data.get("nextPageToken")
        if data.get("isLast", True) or not token:
            break

def value(v):
    if v is None: return ""
    if isinstance(v, dict):
        return v.get("value") or v.get("name") or v.get("displayName") or ""
    return v

def main():
    ids = fields_ids(CUSTOM_FIELDS)
    fields = [ "summary", "status", "priority", "assignee", "created" ] + list(ids.values())

    error_file = "summary_error.txt"
    error_text = ""

    try:
        fileName = f"summary_{date.today():%Y-%m-%d}.csv"
        with open(fileName, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Key", "Summary", "State", "Priority", "Assigned to", "Created at"] + CUSTOM_FIELDS)

            n = 0
            for issue in search(JQL_QUERY, fields):
                fl = issue["fields"]
                w.writerow([
                    issue["key"],
                    fl["summary"],
                    value(fl["status"]),
                    value(fl.get("priority")),
                    value(fl.get("assignee")),
                    fl["created"][:10],
                ] + [value(fl.get(ids[c])) for c in CUSTOM_FIELDS] )
                n += 1

            print(f"[INFO] {n} activities exported to {fileName}")
    except Exception as e:
        with open(error_file, "w", encoding="utf-8") as f:
            f.write(str(e))


if __name__ == "__main__":
    main()