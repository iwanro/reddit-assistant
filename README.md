# Reddit Personal Assistant

Personal automation bot for my own Reddit account (u/Ok_Dot636), built on the
official **Reddit Data API** (OAuth, script-type app, free tier).

## What it does

- **Monitors** new posts in selected subreddits (r/forhire, r/webdev, r/Romania,
  r/programare) and filters them by keywords relevant to me.
- **Sends notifications** (via my own messaging channel) when a matching post appears,
  so I can respond to other Redditors faster.
- **Manages my own activity**: reviews my inbox and helps me reply to comments and
  messages directed at me, so I don't miss questions from the community.

## What it does NOT do

- No mass posting, no mass DMs, no unsolicited contact with other users.
- No user data scraping, no data retention beyond my own notifications.
- Operates **only on my own account** (`u/Ok_Dot636`), within standard free-tier
  rate limits (well under 60 requests/minute).

## Tech

- Python 3.11
- Official Reddit Data API via OAuth2 (`praw` library or raw `requests`)
- Read scope: post monitoring · Identity + read/write: own account management

## Setup (runs locally / on my own server)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in my own OAuth credentials
python monitor.py
```

Credentials are my own script-type app credentials, obtained through Reddit's
Data API registration process. The refresh token is stored locally and never
shared.

## Status

Work in progress — awaiting Reddit Data API access approval.

---

*Submitted as reference for the Reddit Data Access Request (free tier, personal use).*
