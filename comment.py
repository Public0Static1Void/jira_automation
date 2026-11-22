import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_LINK = os.environ["JIRA_BASE"]
AUTH = (os.environ["JIRA_EMAIL"], os.environ["JIRA_TOKEN"])

def comment(key: str, text: str):
    body={
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                { "type": "paragraph", "content": [{ "type": "text", "text": text }] }
            ]
        }
    }
    req = requests.post(
        f"{BASE_LINK}/rest/api/3/issue/{key}/comment",
        json=body,
        auth=AUTH
    )
    req.raise_for_status()
    return req.json()

if __name__ == "__main__":
    try:
        comment(sys.argv[1], sys.argv[2])
        print("Comment added")
    except Exception as e:
        print(f"Error: {e}")