"""
Makes a comment on the activity passed as key.
To execute it call "uvicorn app_app --reload" from your terminal at the directory, then make a curl request.
"""

from fastapi import FastAPI, Request, Header, HTTPException
from comment import comment

import requests
import os
import secrets
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_SECRET=os.environ["WEBHOOK_SECRET"]

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request, x_api_key: str = Header(None)):
    if not x_api_key or not secrets.compare_digest(x_api_key, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Not authorized")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    key = data.get("key")
    summary = data.get("summary", "")

    if not key:
        raise HTTPException(status_code=422, detail="Mising 'key' parameter")

    try:
        comment(key, f"Automatically processed response: {summary}")
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Jira error: {e}")
    
    return { "ok": True }