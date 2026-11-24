# Application and Dependency Inventory

Inventory of the applications, services, libraries and credentials used by this project, with their licences, costs and renewal dates. Review it whenever something is added, removed or changes plan.

_Last reviewed: 2026-11-24_

## 1. Applications and services

| Application | Purpose | Plan / version | Licence model | Monthly cost | Expires / renews | Owner
|---|---|---|---|---|---|---|
| Jira Cloud (Software) | Internal work space `ACT`: workflow, fields, filters, board, dashboard, automation | Free | Per-user subscription (free tier) | 0 € | No expiry | Daniel González
| Jira Service Management | Service desk space `SVC`: portal, queues, escalation rule | 14-day trial | Per-agent subscription | 0 € during the trial | Approx. 2026-12-06 (14 days after activation; confirm in Atlassian Billing) | Daniel González
| Atlassian Administration (admin.atlassian.com) | Users, groups, billing and product access | Included with the site | n/a | 0 € | n/a | Daniel González 
| Jira Cloud REST API (v3) | Integration target for the Python scripts | Included with the site | n/a | 0 € | n/a | Daniel González
| GitHub | Source code and version control | Free | Free tier | 0 € | n/a | Daniel González

## 2. Development tools

| Tool | Purpose | Version | Licence | Cost |
|---|---|---|---|---|
| Python | Runtime for all scripts | 3.14 | PSF License | 0 € |
| pip + venv | Package and environment management | Bundled with Python 3.14 | MIT / PSF | 0 € |
| Visual Studio Code | Editor | Current stable at time of review | Free for use (Microsoft licence) | 0 € |
| Git | Version control | Current stable at time of review | GPL-2.0 | 0 € |

## 3. Python dependencies (direct)

Exact versions are pinned in `requirements.txt`, which is the single source of truth. They are not duplicated here so the two files cannot drift apart.

| Package | Used in | Purpose | Version | Licence |
|---|---|---|---|---|
| `requests` | `comment.py`, `summary.py`, `scraper.py` | HTTP calls to the Jira REST API and to scraped pages | Pinned in `requirements.txt` | Apache-2.0 |
| `fastapi` | `app.py` | Webhook receiver | Pinned in `requirements.txt` | MIT |
| `uvicorn` | `app.py` | ASGI server that runs the webhook service | Pinned in `requirements.txt` | BSD-3-Clause |
| `python-dotenv` | all scripts | Loads secrets from `.env` | Pinned in `requirements.txt` | BSD-3-Clause |
| `beautifulsoup4` | `scraper.py` | HTML parsing for the scraper | Pinned in `requirements.txt` | MIT |

Transitive dependencies (for example those pulled in by FastAPI) are not listed one by one; see `pip freeze` for the full tree.

Licence information above is given from general knowledge; confirm it on each package's PyPI page before relying on it.

## 4. Jira configuration assets

| Asset | Space | Description |
|---|---|---|
| Workflow | `ACT` | `New` → `In review` → `In progress` → `Resolved`, restricted transitions, validators |
| Custom field `Ajuntament` | `ACT`, `SVC` | Select list (`customfield_10046`): Esparraguera, Hospitalet, Cornellà |
| Custom field `Canal d'entrada` | `ACT` | Select list of intake channels. Scripts resolve its ID by name through the API, so the ID is not hard-coded anywhere |
| Queues | `SVC` | Unassigned; open for more than 3 days; by priority |
| Automation rules | `ACT`, `SVC` | Notifications, scheduled stale-request check, escalation from `SVC` to `ACT` |
| Dashboard and filters | `ACT` | Saved JQL filters and dashboard gadgets |
| Scheduled task | Local machine | Weekly run of `summary.py` (Windows Task Scheduler) |

## 5. Dependencies between components

```
Portal (SVC) ──► Escalation rule ──► Task in ACT
                                        ▲
scraper.py ── Jira REST API ────────────┘
app.py ────── Jira REST API ──► Comments on issues
summary.py ── Jira REST API ──► CSV report
```

If the Jira API token is revoked or the site URL changes, every script stops working.