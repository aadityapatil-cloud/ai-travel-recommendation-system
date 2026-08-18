# 🧭 Atlas AI — Tour Recommendation System

A full-stack, AI-powered tour recommendation platform built as a B.Sc. Data Science
college project. It matches users to real Indian destinations using a **content-based
recommendation engine** (TF‑IDF + cosine similarity) blended with **weighted
preference scoring** across 7 criteria — with a transparent, explainable match
percentage for every result.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-black)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.5-orange)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

### 🌐 Live Demo

**[https://ai-travel-recommendation-system.onrender.com/](https://ai-travel-recommendation-system.onrender.com/recommend)**

> Hosted on Render's free tier — the app may take up to 50 seconds to wake up
> on the first request after a period of inactivity.

---

## ✨ Features

- **AI recommendation engine** — TF‑IDF vectorization + cosine similarity for
  soft-matching activities, blended with rule-based scoring for budget, category,
  location, travel style, season, food and accommodation.
- **Explainable match score** — every destination shows an overall AI Match % plus
  a full 7-criteria score breakdown.
- **Modern responsive UI** — Bootstrap 5, custom design system, smooth animations,
  mobile-first layout.
- **Search & filters** — live search, category/region filters, budget cap, sorting.
- **Destination details modal** — full info, activities, and score breakdown.
- **Wishlist / Favorites** — persisted per-session in SQLite, toggle from any card.
- **Interactive analytics dashboard** — Chart.js visualizations (category
  distribution, regional split, average budgets, top-rated destinations).
- **Flask REST API** — clean JSON endpoints for recommendations, destinations,
  wishlist and analytics.
- **Validation & error handling** — client-side and server-side form validation,
  friendly empty/error states, custom 404/500 handling.

---

## 🗂 Project Structure

```
ai-tour-recommendation/
│
├── app.py                     # Flask app, recommender engine, REST APIs
├── requirements.txt           # Python dependencies
├── database.db                # SQLite DB (auto-created on first run)
│
├── dataset/
│   └── destinations.csv       # Sample dataset — 32 Indian destinations
│
├── templates/
│   ├── index.html             # Homepage + preference form
│   └── results.html           # AI recommendations, filters, analytics
│
├── static/
│   ├── css/style.css          # Design system ("Explorer's Atlas")
│   ├── js/script.js           # Front-end logic (fetch, charts, modal, wishlist)
│   └── images/                # (optional local images)
│
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone / download the project
```bash
cd ai-tour-recommendation
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

The database (`database.db`) and its tables are created automatically on first
run, and the sample dataset (`dataset/destinations.csv`) is loaded into SQLite
the first time the app starts.

### 5. Open in your browser
```
http://127.0.0.1:5000
```

That's it — no manual database setup needed. Fully VS Code compatible.

Prefer not to install anything locally? Use the live demo linked above instead.

---

## 🧠 How the Recommendation Engine Works

`TourRecommender` (in `app.py`) computes, for every destination, a score
between 0–1 for each of 7 criteria, then combines them with fixed weights:

| Criterion              | Weight | Method                                                             |
|-------------------------|:------:|---------------------------------------------------------------------|
| Budget Match             | 30%   | Normalized closeness between user's budget/day and destination cost |
| Category Match           | 25%   | Exact match on destination category                                 |
| Activities Match         | 20%   | **TF‑IDF + cosine similarity** between selected & offered activities|
| Location Match           | 10%   | Match against destination region/state                              |
| Travel Style Match       | 5%    | Exact match (Solo, Family, Couple, Group, Backpacker, Luxury)        |
| Season Match             | 5%    | Match against best travel season                                    |
| Food & Accommodation     | 5%    | Combined food-type and stay-type match                              |

```
final_score = Σ (criterion_score × criterion_weight) × 100
```

The **Activities Match** is the true "content-based" component: each
destination's activity list is vectorized with `TfidfVectorizer`, and the
user's selected activities are transformed into the same vector space, then
compared with `cosine_similarity` — so a user who picks "Trekking, Camping,
Photography" will score highly against destinations with overlapping and
semantically related activity text, not just exact string matches.

---

## 🔌 REST API Reference

| Method | Endpoint                        | Description                                  |
|--------|----------------------------------|-----------------------------------------------|
| GET    | `/`                              | Homepage with preference form                |
| POST   | `/recommend`                     | Server-rendered results page (form submit)   |
| POST   | `/api/recommend`                 | JSON recommendations for given preferences   |
| GET    | `/api/destinations`              | Search/filter/sort all destinations          |
| GET    | `/api/destination/<id>`          | Full detail for one destination              |
| GET    | `/api/wishlist`                  | Current session's wishlist                   |
| POST   | `/api/wishlist/toggle`           | Add/remove a destination from wishlist       |
| DELETE | `/api/wishlist/<id>`             | Remove a destination from wishlist           |
| GET    | `/api/analytics`                 | Aggregated stats for the analytics dashboard |
| GET    | `/api/form-options`              | Dropdown values (categories, regions, etc.)  |

**Example — `POST /api/recommend`:**
```json
{
  "preferred_location": "North India",
  "category": "Hill Station",
  "budget": 25000,
  "travel_days": 5,
  "travel_season": "Summer",
  "travel_style": "Family",
  "activities": ["Trekking", "Sightseeing", "Photography"],
  "travelers": 2,
  "food_preference": "Veg",
  "accommodation": "Mid-range"
}
```

---

## 🛠 Tech Stack

| Layer            | Technology                                             |
|-------------------|--------------------------------------------------------|
| Frontend          | HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Font Awesome, Chart.js |
| Backend           | Python 3, Flask, REST API                              |
| Database          | SQLite (`sqlite3`)                                      |
| Data Science      | pandas, NumPy, scikit-learn (`TfidfVectorizer`, `cosine_similarity`) |
| Deployment        | Docker + Render                                         |

---

## 📊 Dataset

`dataset/destinations.csv` contains 32 real Indian destinations spanning 6
regions, 9 categories, 4 seasons and 6 travel styles — enough variety to
demonstrate meaningful, differentiated recommendations. Swap in your own CSV
(same columns) and delete `database.db` to reseed with new data.

---

## 🎓 Notes for Submission / Portfolio

- Replace the placeholder Unsplash image URLs in `destinations.csv` with your
  own hosted images if you need the project to work fully offline.
- The wishlist and search history use a lightweight per-browser session ID
  (via Flask's signed cookie session) — no login system was required for the
  scope of this project, but the `search_history` table already captures
  every query for potential future analysis (e.g. most-requested categories).
- To reset the database, simply delete `database.db` and restart the app —
  it will be rebuilt from `dataset/destinations.csv` automatically.

---

Built for a B.Sc. Data Science coursework & GitHub portfolio submission.