#!/usr/bin/env python3
"""Personal Reddit assistant: monitor subreddits for relevant new posts.

Runs on my own account (u/Ok_Dot636) via the official Reddit Data API.
Read-only monitoring: fetches new posts from a small set of subreddits,
filters by keyword, and notifies me through my own messaging channel
(webhook). Rate-limit friendly: one batch check every few minutes,
well within free tier limits.
"""

import os
import time
import logging

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("reddit-assistant")

REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME", "iwanro-assistant")
USER_AGENT = f"script:personal.assistant:v0.1 (by /u/{REDDIT_USERNAME})"

# Subreddits I follow and want to monitor for new posts
SUBREDDITS = ["forhire", "webdev", "Romania", "programare"]

# Keywords relevant to my work (web/mobile development)
KEYWORDS = ["website", "web app", "android", "flutter", "app developer", "site"]

# Where I get notified (my own private webhook)
NOTIFY_WEBHOOK = os.environ.get("NOTIFY_WEBHOOK", "")

POLL_INTERVAL_SEC = 300  # 5 minutes — very conservative vs. free tier limits


def get_reddit_token() -> str:
    """OAuth password grant for my own script-type app (standard Data API flow)."""
    client_id = os.environ["REDDIT_CLIENT_ID"]
    client_secret = os.environ["REDDIT_CLIENT_SECRET"]
    resp = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(client_id, client_secret),
        data={
            "grant_type": "password",
            "username": REDDIT_USERNAME,
            "password": os.environ["REDDIT_PASSWORD"],
        },
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_new_posts(token: str, subreddit: str, limit: int = 10) -> list:
    resp = requests.get(
        f"https://oauth.reddit.com/r/{subreddit}/new",
        headers={"Authorization": f"bearer {token}", "User-Agent": USER_AGENT},
        params={"limit": limit},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("data", {}).get("children", [])


def matches(post_data: dict) -> bool:
    text = f"{post_data.get('title', '')} {post_data.get('selftext', '')}".lower()
    return any(k.lower() in text for k in KEYWORDS)


def notify(post_data: dict, subreddit: str) -> None:
    """Notify me through my own private messaging webhook."""
    if not NOTIFY_WEBHOOK:
        log.info("[notify disabled] r/%s: %s", subreddit, post_data.get("title"))
        return
    requests.post(
        NOTIFY_WEBHOOK,
        json={
            "text": (
                f"r/{subreddit}: {post_data.get('title')}\n"
                f"https://reddit.com{post_data.get('permalink', '')}"
            )
        },
        timeout=10,
    )


def run_once() -> None:
    token = get_reddit_token()
    for sub in SUBREDDITS:
        try:
            for child in fetch_new_posts(token, sub):
                data = child.get("data", {})
                if matches(data):
                    notify(data, sub)
        except requests.RequestException as exc:
            log.warning("fetch failed for r/%s: %s", sub, exc)
        time.sleep(1.1)  # polite spacing between subreddits


if __name__ == "__main__":
    log.info("starting monitor for u/%s (read-only, free tier)", REDDIT_USERNAME)
    while True:
        run_once()
        time.sleep(POLL_INTERVAL_SEC)
