"""
Makes a request to the Jira server using the API and prints all the activities
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_LINK = os.environ["JIRA_BASE"]
AUTH = (os.environ["JIRA_EMAIL"], os.environ["JIRA_TOKEN"])

req = requests.get(
    f"{BASE_LINK}/rest/api/3/search/jql",
    params={
        "jql": "project = ACT AND status != Resolt ORDER BY created DESC",
        "fields": "summary,status",
        "maxResults": 20
    },
    auth=AUTH,
    headers={"Accept": "application/json"}
)
req.raise_for_status()

for issue in req.json()["issues"]:
    f = issue["fields"]
    print(issue["key"], "\t|\t", f["status"]["name"], "\t|\t", f["summary"])