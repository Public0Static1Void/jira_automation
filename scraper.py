import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
BASE_LINK = os.environ["JIRA_BASE"]
AUTH = (os.environ["JIRA_EMAIL"], os.environ["JIRA_TOKEN"])

# Site to scrap
SOURCE_URL = "https://books.toscrape.com"
ITEM_SELECTOR = "article.product_pod"       # CSS selector
LINK_SELECTOR = "h3 a"                      # link inside each item

PROJECT_KEY = "ACT"
ISSUE_TYPE = "Tarea"

FIELD_VALUES = { "Ajuntament": "Esparraguera", "Canal d'entrada": "Web" }

SEEN_FILE = Path("seen.json")
USER_AGENT = "jira-automation-practice/1.0 (educational project)"

def allowed_by_robots(url):
    parts = urlparse(url)
    rp = RobotFileParser()
    rp.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
    rp.read()
    return rp.can_fetch(USER_AGENT, url)

def scrape():
    if not allowed_by_robots(SOURCE_URL):
        sys.exit("robots.txt doesn't allow scraping this URL. Stopping the code")

    req = requests.get(SOURCE_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
    req.raise_for_status()
    soup = BeautifulSoup(req.content, "html.parser")

    items = []
    for node in soup.select(ITEM_SELECTOR):
        link = node.select_one(LINK_SELECTOR)
        if not link: continue

        title = (link.get("title") or link.get_text()).strip()
        href = urljoin(SOURCE_URL, link.get("href", ""))
        if title and href:
            items.append({"title": title, "url": href})

    if not items:
        sys.exit("No items found.\nPage structure may have changed.\n\nPlease review ITEM_SELECTOR and LINK_SELECTOR")
    return items

def field_ids(names):
    req = requests.get(f"{BASE_LINK}/rest/api/3/field", auth=AUTH)
    req.raise_for_status()

    by_name = { f["name"]: f["id"] for f in req.json() }
    missing = [ n for n in names if n not in by_name ]
    if missing:
        sys.exit(f"Custom fields not found in Jira: {missing}")

    return { n: by_name[n] for n in names }

def create_issue(item, ids):
    fields = {
        "project": { "key": PROJECT_KEY },
        "issuetype": { "name": ISSUE_TYPE },
        "summary": item["title"][:250],
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        { "type": "text", "text": "Found by scraper: " },
                        {
                            "type": "text",
                            "text": item["url"],
                            "marks": [{ "type": "link", "attrs": { "href": item["url"] } }]
                        }
                    ]
                }
            ]
        }
    }

    for name, value in FIELD_VALUES.items():
        fields[ids[name]] = { "value": value }

    req = requests.post(f"{BASE_LINK}/rest/api/3/issue", json={"fields": fields}, auth=AUTH)
    if not req.ok:
        print(req.status_code, req.text)

    req.raise_for_status()
    return req.json()["key"]

def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()

def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Only prints the results instead of pushing them to Jira")
    parser.add_argument("--limit", type=int, default=5, help="Result limit")

    args = parser.parse_args()

    items = scrape()
    seen = load_seen()

    new_items = [ i for i in items if i["url"] not in seen ][: args.limit]

    if args.dry_run:
        for item in new_items:
            print(f"\t- {item['title']}: {item['url']}")
        return

    if not new_items: return

    ids = field_ids(FIELD_VALUES.keys())
    for item in new_items:
        key = create_issue(item, ids)
        seen.add(item["url"])
        save_seen(seen)
        print(f"Item {key} saved.\nTitle: {item['title']}\nURL: {item['url']}")


if __name__ == "__main__":
    main()