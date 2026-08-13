#  LaughLoop — Personalized Joke Recommender

LaughLoop is a full-stack web application that learns an individual user's sense of humor from real interaction data and delivers increasingly personalized joke recommendations — built end-to-end as a solo project spanning dataset curation, ML-based content classification, backend API design, and cloud deployment.

**Live site:** [laughloop1.vercel.app](https://laughloop1.vercel.app)

---

## About the Project

Most joke apps show the same content to everyone. LaughLoop instead treats humor as a personalization problem: every like, dislike, save, and second spent reading a joke feeds into a live profile of what a specific user actually finds funny, and the recommendation engine adapts accordingly — in real time, not just at signup.

The project was built to explore how a lightweight, interpretable recommendation system could be trained on a real dataset and deployed as a genuine production service, rather than a notebook demo.

---

## How It Was Built

**Dataset.** Sourced ~38,000 question–answer jokes from the r/Jokes subreddit dataset. Cleaned and filtered the corpus to remove explicit/inappropriate content using pattern-based text filtering before it ever reached the live database.

**Categorization (ML).** Jokes needed category labels (Puns, Dark, Programming, Sports, etc.) before any recommendation logic could use them. A text classifier was trained on labeled joke samples to automatically assign each joke in the dataset to a category, using TF-IDF-style feature extraction and a supervised classification model — avoiding the need to manually tag tens of thousands of entries by hand.

**Backend.** Designed a relational schema (users, jokes, categories, interactions, preferences) and built a FastAPI service on top of it, with JWT authentication, hashed password storage, and a set of endpoints for jokes, interactions, recommendations, and explanations.

**Recommendation logic.** Rather than a black-box model, the recommender uses transparent, auditable logic: it aggregates a user's liked-joke categories and serves jokes from whichever category currently has the most engagement. This was a deliberate choice for interpretability and speed of iteration in v1, with a heavier collaborative-filtering model planned as a future upgrade (see Roadmap).

**Deployment.** Iterated through two full deployment architectures — first a self-hosted setup on a Raspberry Pi 5 (systemd services, local MariaDB, SSH-based management), then migrated to a cloud-native stack (Vercel + managed MySQL) once the constraint of requiring guaranteed 24/7 power/network for a public site became clear. The Pi is retained for future offline model retraining work.

---

## Features

- **Random & recommended jokes** — pulled fresh from a 38K+ joke database
- **Like / dislike** — every reaction is logged and immediately affects future recommendations
- **Save jokes** — build a personal collection, viewable and removable at any time
- **AI joke explanations** — one click generates a plain-English breakdown of the wordplay, powered by Gemini
- **Live preferences chart** — a visual bar-per-category breakdown of your humor profile
- **Light / dark theme** — full UI theme toggle, persisted per session
- **JWT authentication** — signup/login with hashed password storage

---

## How Personalization Works

Your **Preferences** chart is built by counting, per category, how many jokes in that category you've liked. A category with more likes gets a longer bar. The next joke you're recommended is pulled from whichever category currently has the most likes in your history — so the system is always reading your most recent behavior, not a fixed profile set once at signup.

**Why deleting a saved joke lowers that category's preference.** Saving/liking a joke and having it counted in your preferences are linked through the same underlying interaction record. When you remove a saved joke, its associated `liked` interaction is removed too — so it no longer counts toward that category's total. The bar for that category shrinks on your next preferences load, because the count behind it genuinely went down.

This means your preferences aren't a one-time snapshot — they're a live tally of your current interaction history. Delete enough jokes from a category, and it stops looking like something you're into.

**Why you can deliberately reshape your chart.** Because the whole system is just counting live interactions, you're in full control of it:

- Like 10 jokes in the Dark category → Dark becomes your dominant bar → you start getting recommended more Dark jokes
- Get bored of that, unsave/dislike those same jokes, and like 10 Programming jokes instead → your chart flips → recommendations follow
- There's no "locked in" personality here — the chart is a direct, real-time reflection of what you've recently told the system you enjoy, and it updates the moment you change that behavior

In short: your preferences chart isn't a label the AI assigns you — it's a running total you're actively building (or dismantling) every time you tap like, dislike, or remove a save.

---

## Tech Stack

**Frontend:** React (Vite), Axios, custom CSS with light/dark theming

**Backend:** FastAPI, SQLAlchemy ORM, JWT auth (`python-jose`), password hashing (`passlib` + `bcrypt`), Google Gemini API for joke explanations

**ML/Data:** Text classification for automated joke categorization, trained on labeled samples with scikit-learn

**Database:** MySQL, hosted on Aiven (managed cloud)

**Deployment:** Vercel, single project with multi-service routing (`/api/*` → backend, everything else → frontend) under one public URL

---

## API Overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/signup` | POST | Create account |
| `/api/login` | POST | Authenticate, returns JWT |
| `/api/jokes/random` | GET | Fetch a random joke |
| `/api/interactions/` | POST | Log a like/dislike/rating |
| `/api/interactions/saved` | GET | List all jokes the user has liked/saved |
| `/api/recommendations/{user_id}` | GET | Get a joke from the user's top category |
| `/api/preferences/{user_id}` | GET | Get category-wise like counts for the chart |
| `/api/explain` | POST | Get a plain-English explanation of a joke |

---

## Roadmap

- Replace category-counting recommendations with a collaborative-filtering or LSTM-based model trained on accumulated interaction data
- Use the Raspberry Pi as a dedicated offline retraining worker — periodically pulling interaction data from the cloud database, retraining, and pushing updated model weights back — decoupling heavy computation from the always-on serverless deployment
- Tighten CORS/rate-limiting for production hardening

---

## Credits

Joke dataset sourced from r/Jokes (Reddit), question–answer format, ~38K entries.
