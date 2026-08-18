"""
AI Tour Recommendation System
------------------------------
A Flask + SQLite + scikit-learn powered travel recommendation platform.

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import os
import sqlite3
import uuid
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, g, jsonify, render_template, request, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------
# App configuration
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")
DATASET_CSV = os.path.join(BASE_DIR, "dataset", "destinations.csv")

app = Flask(__name__)
app.config["SECRET_KEY"] = "ai-tour-recommendation-secret-key-2026"
app.config["DATABASE"] = DATABASE

MULTI_VALUE_FIELDS = ["activities"]

# --------------------------------------------------------------------------
# Database helpers
# --------------------------------------------------------------------------


def get_db():
    """Open a new database connection if there is none yet for the request."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables (if needed) and seed destinations from the CSV dataset."""
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            state TEXT,
            region TEXT,
            category TEXT,
            budget_per_day INTEGER,
            min_days INTEGER,
            max_days INTEGER,
            best_season TEXT,
            travel_style TEXT,
            activities TEXT,
            food_type TEXT,
            accommodation TEXT,
            description TEXT,
            image_url TEXT,
            rating REAL,
            popularity INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            destination_id INTEGER NOT NULL,
            added_at TEXT NOT NULL,
            UNIQUE(session_id, destination_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            preferred_location TEXT,
            category TEXT,
            budget INTEGER,
            travel_days INTEGER,
            travel_season TEXT,
            travel_style TEXT,
            activities TEXT,
            travelers INTEGER,
            food_preference TEXT,
            accommodation TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    db.commit()

    # Always re-sync the destinations table from the CSV on startup.
    # This keeps deployments (e.g. on Render) in lockstep with dataset edits —
    # otherwise a stale database.db could silently keep serving old/broken
    # data (like outdated image URLs) even after the CSV is fixed and redeployed.
    # wishlist/search_history reference destinations by their stable CSV "id",
    # so replacing rows (not the table itself) keeps those references valid.
    df = pd.read_csv(DATASET_CSV)
    cur.execute("DELETE FROM destinations")
    df.to_sql("destinations", db, if_exists="append", index=False)
    db.commit()
    db.close()


# --------------------------------------------------------------------------
# Recommendation engine
# --------------------------------------------------------------------------
class TourRecommender:
    """
    Content-based recommendation engine.

    Two signals are combined:
      1. Soft "semantic" matching for free-form multi-value fields
         (activities) using TfidfVectorizer + cosine_similarity.
      2. Rule-based preference scoring for structured fields
         (budget, category, location, style, season, food, accommodation).

    The final score is a weighted blend of all 7 criteria, matching the
    project brief exactly:
        Budget Match        - 30%
        Category Match      - 25%
        Activities Match    - 20%
        Location Match      - 10%
        Travel Style Match  - 5%
        Season Match        - 5%
        Food & Accommodation- 5%
    """

    WEIGHTS = {
        "budget": 0.30,
        "category": 0.25,
        "activities": 0.20,
        "location": 0.10,
        "style": 0.05,
        "season": 0.05,
        "food_accom": 0.05,
    }

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.reset_index(drop=True).copy()
        self.df["activities_list"] = self.df["activities"].apply(
            lambda s: [a.strip().lower() for a in str(s).split(",")]
        )
        # Build the TF-IDF corpus from each destination's activity text.
        self.corpus = self.df["activities"].fillna("").astype(str).tolist()
        self.vectorizer = TfidfVectorizer(token_pattern=r"[a-zA-Z]+")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    # ---- individual scoring functions (each returns 0.0 - 1.0) ----------

    def _budget_score(self, dest_budget: float, user_budget_per_day: float) -> float:
        if user_budget_per_day <= 0:
            return 0.0
        diff_ratio = abs(dest_budget - user_budget_per_day) / user_budget_per_day
        # Full score for an exact match, decaying linearly, 0 beyond 80% difference.
        return float(max(0.0, 1.0 - diff_ratio / 0.8))

    def _category_score(self, dest_category: str, user_category: str) -> float:
        if not user_category or user_category.lower() == "any":
            return 0.7  # neutral-positive score when user has no strong preference
        return 1.0 if dest_category.lower() == user_category.lower() else 0.15

    def _activities_score(self, dest_index: int, user_activities: list) -> float:
        if not user_activities:
            return 0.5
        user_text = " ".join(user_activities)
        user_vec = self.vectorizer.transform([user_text])
        dest_vec = self.tfidf_matrix[dest_index]
        sim = cosine_similarity(user_vec, dest_vec)[0][0]
        return float(sim)

    def _location_score(self, dest_region: str, dest_state: str, user_location: str) -> float:
        if not user_location or user_location.lower() == "any":
            return 0.6
        user_location = user_location.lower().strip()
        if user_location in dest_region.lower() or user_location in dest_state.lower():
            return 1.0
        return 0.1

    def _style_score(self, dest_style: str, user_style: str) -> float:
        if not user_style or user_style.lower() == "any":
            return 0.7
        return 1.0 if dest_style.lower() == user_style.lower() else 0.2

    def _season_score(self, dest_season: str, user_season: str) -> float:
        if not user_season or user_season.lower() == "any":
            return 0.7
        if dest_season.lower() == user_season.lower() or dest_season.lower() == "year-round":
            return 1.0
        return 0.25

    def _food_accom_score(self, dest_food: str, dest_accom: str, user_food: str, user_accom: str) -> float:
        food_score = 0.7
        accom_score = 0.7
        if user_food and user_food.lower() != "any":
            if dest_food.lower() == "both" or dest_food.lower() == user_food.lower():
                food_score = 1.0
            else:
                food_score = 0.2
        if user_accom and user_accom.lower() != "any":
            accom_score = 1.0 if dest_accom.lower() == user_accom.lower() else 0.2
        return (food_score + accom_score) / 2.0

    # ---- main entry point -------------------------------------------------

    def recommend(self, prefs: dict, top_n: int = 12) -> list:
        travel_days = max(1, int(prefs.get("travel_days") or 1))
        travelers = max(1, int(prefs.get("travelers") or 1))
        total_budget = float(prefs.get("budget") or 0)
        user_budget_per_day = total_budget / travel_days / travelers if total_budget else 0

        user_activities = [a.strip().lower() for a in prefs.get("activities", []) if a.strip()]

        results = []
        for idx, row in self.df.iterrows():
            budget_s = self._budget_score(row["budget_per_day"], user_budget_per_day) if user_budget_per_day else 0.6
            category_s = self._category_score(row["category"], prefs.get("category", ""))
            activities_s = self._activities_score(idx, user_activities)
            location_s = self._location_score(row["region"], row["state"], prefs.get("preferred_location", ""))
            style_s = self._style_score(row["travel_style"], prefs.get("travel_style", ""))
            season_s = self._season_score(row["best_season"], prefs.get("travel_season", ""))
            food_accom_s = self._food_accom_score(
                row["food_type"], row["accommodation"],
                prefs.get("food_preference", ""), prefs.get("accommodation", "")
            )

            final = (
                budget_s * self.WEIGHTS["budget"]
                + category_s * self.WEIGHTS["category"]
                + activities_s * self.WEIGHTS["activities"]
                + location_s * self.WEIGHTS["location"]
                + style_s * self.WEIGHTS["style"]
                + season_s * self.WEIGHTS["season"]
                + food_accom_s * self.WEIGHTS["food_accom"]
            )
            score_pct = round(final * 100, 1)

            item = row.drop(labels=["activities_list"]).to_dict()
            item["match_score"] = score_pct
            item["score_breakdown"] = {
                "budget": round(budget_s * 100, 1),
                "category": round(category_s * 100, 1),
                "activities": round(activities_s * 100, 1),
                "location": round(location_s * 100, 1),
                "travel_style": round(style_s * 100, 1),
                "season": round(season_s * 100, 1),
                "food_accommodation": round(food_accom_s * 100, 1),
            }
            item["suggested_total_cost"] = int(row["budget_per_day"] * travel_days * travelers)
            results.append(item)

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:top_n]


# Load dataset into the recommender once at startup.
_recommender = None


def get_recommender():
    global _recommender
    if _recommender is None:
        db = sqlite3.connect(app.config["DATABASE"])
        df = pd.read_sql_query("SELECT * FROM destinations", db)
        db.close()
        _recommender = TourRecommender(df)
    return _recommender


# --------------------------------------------------------------------------
# Session helper (lightweight, no-login "session id" for wishlist/history)
# --------------------------------------------------------------------------
def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def validate_preferences(data: dict):
    errors = {}

    def to_number(key, positive=True):
        val = data.get(key)
        try:
            num = float(val)
            if positive and num <= 0:
                errors[key] = f"{key.replace('_', ' ').title()} must be greater than 0."
            return num
        except (TypeError, ValueError):
            errors[key] = f"{key.replace('_', ' ').title()} is required and must be a number."
            return None

    to_number("budget")
    to_number("travel_days")
    to_number("travelers")

    if not data.get("category"):
        errors["category"] = "Please select a destination category."

    return errors


# --------------------------------------------------------------------------
# Page routes
# --------------------------------------------------------------------------
@app.route("/")
def index():
    db = get_db()
    categories = [r["category"] for r in db.execute("SELECT DISTINCT category FROM destinations ORDER BY category")]
    regions = [r["region"] for r in db.execute("SELECT DISTINCT region FROM destinations ORDER BY region")]
    styles = [r["travel_style"] for r in db.execute("SELECT DISTINCT travel_style FROM destinations ORDER BY travel_style")]
    seasons = [r["best_season"] for r in db.execute("SELECT DISTINCT best_season FROM destinations ORDER BY best_season")]
    activities_raw = [r["activities"] for r in db.execute("SELECT activities FROM destinations")]
    all_activities = sorted({a.strip() for row in activities_raw for a in row.split(",")})
    foods = [r["food_type"] for r in db.execute("SELECT DISTINCT food_type FROM destinations ORDER BY food_type")]
    accoms = [r["accommodation"] for r in db.execute("SELECT DISTINCT accommodation FROM destinations ORDER BY accommodation")]

    return render_template(
        "index.html",
        categories=categories,
        regions=regions,
        styles=styles,
        seasons=seasons,
        activities=all_activities,
        foods=foods,
        accoms=accoms,
    )


@app.route("/recommend", methods=["POST"])
def recommend_page():
    """Server-rendered results page (classic form submit, no JS required)."""
    form = request.form
    prefs = {
        "preferred_location": form.get("preferred_location", "").strip(),
        "category": form.get("category", "").strip(),
        "budget": form.get("budget", "0"),
        "travel_days": form.get("travel_days", "1"),
        "travel_season": form.get("travel_season", "").strip(),
        "travel_style": form.get("travel_style", "").strip(),
        "activities": form.getlist("activities"),
        "travelers": form.get("travelers", "1"),
        "food_preference": form.get("food_preference", "").strip(),
        "accommodation": form.get("accommodation", "").strip(),
    }

    errors = validate_preferences(prefs)
    if errors:
        return render_template("index.html", errors=errors, form_data=prefs), 400

    recommender = get_recommender()
    recommendations = recommender.recommend(prefs, top_n=12)
    save_search_history(prefs)

    return render_template(
        "results.html",
        recommendations=recommendations,
        prefs=prefs,
    )


def save_search_history(prefs):
    db = get_db()
    db.execute(
        """INSERT INTO search_history
        (session_id, preferred_location, category, budget, travel_days, travel_season,
         travel_style, activities, travelers, food_preference, accommodation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            get_session_id(),
            prefs.get("preferred_location"),
            prefs.get("category"),
            int(float(prefs.get("budget") or 0)),
            int(float(prefs.get("travel_days") or 0)),
            prefs.get("travel_season"),
            prefs.get("travel_style"),
            ",".join(prefs.get("activities", [])),
            int(float(prefs.get("travelers") or 1)),
            prefs.get("food_preference"),
            prefs.get("accommodation"),
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()


# --------------------------------------------------------------------------
# REST API routes
# --------------------------------------------------------------------------
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json(silent=True) or {}
    errors = validate_preferences(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    recommender = get_recommender()
    recommendations = recommender.recommend(data, top_n=int(data.get("top_n", 12)))
    save_search_history(data)

    return jsonify({"success": True, "count": len(recommendations), "results": recommendations})


@app.route("/api/destinations", methods=["GET"])
def api_destinations():
    """List / search / filter destinations. Used by the results page filter bar."""
    db = get_db()
    query = "SELECT * FROM destinations WHERE 1=1"
    params = []

    search = request.args.get("search", "").strip()
    if search:
        query += " AND (LOWER(name) LIKE ? OR LOWER(state) LIKE ? OR LOWER(description) LIKE ?)"
        like = f"%{search.lower()}%"
        params += [like, like, like]

    category = request.args.get("category", "").strip()
    if category and category.lower() != "any":
        query += " AND category = ?"
        params.append(category)

    region = request.args.get("region", "").strip()
    if region and region.lower() != "any":
        query += " AND region = ?"
        params.append(region)

    budget_max = request.args.get("budget_max", "").strip()
    if budget_max:
        try:
            query += " AND budget_per_day <= ?"
            params.append(float(budget_max))
        except ValueError:
            pass

    min_days = request.args.get("min_days", "").strip()
    if min_days:
        try:
            query += " AND max_days >= ?"
            params.append(float(min_days))
        except ValueError:
            pass

    sort = request.args.get("sort", "popularity")
    sort_map = {
        "popularity": "popularity DESC",
        "rating": "rating DESC",
        "budget_low": "budget_per_day ASC",
        "budget_high": "budget_per_day DESC",
        "name": "name ASC",
    }
    query += f" ORDER BY {sort_map.get(sort, 'popularity DESC')}"

    rows = db.execute(query, params).fetchall()
    results = [dict(r) for r in rows]
    return jsonify({"success": True, "count": len(results), "results": results})


@app.route("/api/destination/<int:dest_id>", methods=["GET"])
def api_destination_detail(dest_id):
    db = get_db()
    row = db.execute("SELECT * FROM destinations WHERE id = ?", (dest_id,)).fetchone()
    if row is None:
        return jsonify({"success": False, "error": "Destination not found."}), 404
    return jsonify({"success": True, "result": dict(row)})


@app.route("/api/wishlist", methods=["GET"])
def api_wishlist_get():
    db = get_db()
    sid = get_session_id()
    rows = db.execute(
        """SELECT d.* FROM wishlist w
           JOIN destinations d ON d.id = w.destination_id
           WHERE w.session_id = ?
           ORDER BY w.added_at DESC""",
        (sid,),
    ).fetchall()
    return jsonify({"success": True, "count": len(rows), "results": [dict(r) for r in rows]})


@app.route("/api/wishlist/toggle", methods=["POST"])
def api_wishlist_toggle():
    data = request.get_json(silent=True) or {}
    dest_id = data.get("destination_id")
    if not dest_id:
        return jsonify({"success": False, "error": "destination_id is required."}), 400

    db = get_db()
    sid = get_session_id()
    existing = db.execute(
        "SELECT id FROM wishlist WHERE session_id = ? AND destination_id = ?", (sid, dest_id)
    ).fetchone()

    if existing:
        db.execute("DELETE FROM wishlist WHERE id = ?", (existing["id"],))
        db.commit()
        return jsonify({"success": True, "action": "removed"})
    else:
        db.execute(
            "INSERT INTO wishlist (session_id, destination_id, added_at) VALUES (?, ?, ?)",
            (sid, dest_id, datetime.utcnow().isoformat()),
        )
        db.commit()
        return jsonify({"success": True, "action": "added"})


@app.route("/api/wishlist/<int:dest_id>", methods=["DELETE"])
def api_wishlist_delete(dest_id):
    db = get_db()
    sid = get_session_id()
    db.execute("DELETE FROM wishlist WHERE session_id = ? AND destination_id = ?", (sid, dest_id))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/analytics", methods=["GET"])
def api_analytics():
    db = get_db()

    by_category = db.execute(
        "SELECT category, COUNT(*) AS count, ROUND(AVG(budget_per_day),0) AS avg_budget "
        "FROM destinations GROUP BY category ORDER BY count DESC"
    ).fetchall()

    by_region = db.execute(
        "SELECT region, COUNT(*) AS count FROM destinations GROUP BY region ORDER BY count DESC"
    ).fetchall()

    by_season = db.execute(
        "SELECT best_season, COUNT(*) AS count FROM destinations GROUP BY best_season ORDER BY count DESC"
    ).fetchall()

    top_rated = db.execute(
        "SELECT name, rating, popularity FROM destinations ORDER BY rating DESC, popularity DESC LIMIT 8"
    ).fetchall()

    budget_range = db.execute(
        "SELECT MIN(budget_per_day) AS min_b, MAX(budget_per_day) AS max_b, "
        "ROUND(AVG(budget_per_day),0) AS avg_b FROM destinations"
    ).fetchone()

    return jsonify(
        {
            "success": True,
            "by_category": [dict(r) for r in by_category],
            "by_region": [dict(r) for r in by_region],
            "by_season": [dict(r) for r in by_season],
            "top_rated": [dict(r) for r in top_rated],
            "budget_range": dict(budget_range),
        }
    )


@app.route("/api/form-options", methods=["GET"])
def api_form_options():
    db = get_db()
    categories = [r["category"] for r in db.execute("SELECT DISTINCT category FROM destinations ORDER BY category")]
    regions = [r["region"] for r in db.execute("SELECT DISTINCT region FROM destinations ORDER BY region")]
    styles = [r["travel_style"] for r in db.execute("SELECT DISTINCT travel_style FROM destinations ORDER BY travel_style")]
    seasons = [r["best_season"] for r in db.execute("SELECT DISTINCT best_season FROM destinations ORDER BY best_season")]
    activities_raw = [r["activities"] for r in db.execute("SELECT activities FROM destinations")]
    all_activities = sorted({a.strip() for row in activities_raw for a in row.split(",")})
    return jsonify(
        {
            "success": True,
            "categories": categories,
            "regions": regions,
            "styles": styles,
            "seasons": seasons,
            "activities": all_activities,
        }
    )


# --------------------------------------------------------------------------
# Error handlers
# --------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Resource not found."}), 404
    return render_template("index.html", errors={}, form_data={}), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error."}), 500
    return render_template("index.html", errors={"server": "Something went wrong. Please try again."}, form_data={}), 500


# --------------------------------------------------------------------------
# Database initialisation
# --------------------------------------------------------------------------
# This must run at import time (not just inside `if __name__ == "__main__"`)
# because production servers like gunicorn import this module directly and
# never execute the __main__ block. Without this, Render would boot the app
# with an empty/missing destinations table.
init_db()


# --------------------------------------------------------------------------
# Entry point (local development only — Render uses gunicorn instead)
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
