import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Scoring mode weight presets  (Challenge 2: Multiple Scoring Modes)
# Each key maps to a weights dict used by _score_against_profile.
# ---------------------------------------------------------------------------
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced":       {"genre": 2.0, "mood": 1.0, "energy": 1.0, "acoustic": 0.5, "popularity": 0.3, "decade": 0.2, "mood_tags": 0.5},
    "genre_first":    {"genre": 4.0, "mood": 0.5, "energy": 0.3, "acoustic": 0.3, "popularity": 0.2, "decade": 0.1, "mood_tags": 0.3},
    "mood_first":     {"genre": 1.0, "mood": 3.0, "energy": 0.5, "acoustic": 0.3, "popularity": 0.3, "decade": 0.1, "mood_tags": 1.0},
    "energy_focused": {"genre": 0.5, "mood": 0.5, "energy": 3.0, "acoustic": 0.3, "popularity": 0.2, "decade": 0.1, "mood_tags": 0.3},
}


@dataclass
class Song:
    """Represents a song and its attributes. Required by tests/test_recommender.py"""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Challenge 1: advanced features (default values keep existing tests passing)
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: str = ""


@dataclass
class UserProfile:
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Challenge 1 / 2: optional extended preferences
    target_popularity: int = 50
    preferred_decade: int = 0          # 0 = no decade preference
    favorite_mood_tags: str = ""       # comma-separated, e.g. "euphoric,nostalgic"
    scoring_mode: str = "balanced"


# ---------------------------------------------------------------------------
# Core scoring engine
# ---------------------------------------------------------------------------

def _score_against_profile(
    genre: str, mood: str, energy: float, acousticness: float,
    popularity: int, release_decade: int, mood_tags: str,
    fav_genre: str, fav_mood: str, target_energy: float,
    likes_acoustic: bool, target_popularity: int = 50,
    preferred_decade: int = 0, favorite_mood_tags: str = "",
    mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """Shared scoring logic for both OOP and functional APIs. Supports all scoring modes."""
    weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    score = 0.0
    reasons = []

    # Genre match (exact string)
    if genre.lower() == fav_genre.lower():
        pts = weights["genre"]
        score += pts
        reasons.append(f"genre match ({genre}, +{pts:.1f})")

    # Mood match (exact string)
    if mood.lower() == fav_mood.lower():
        pts = weights["mood"]
        score += pts
        reasons.append(f"mood match ({mood}, +{pts:.1f})")

    # Energy similarity — continuous reward for closeness
    energy_sim = 1.0 - abs(energy - target_energy)
    pts = energy_sim * weights["energy"]
    score += pts
    reasons.append(f"energy similarity ({energy_sim:.2f}, +{pts:.2f})")

    # Acoustic preference bonus
    if likes_acoustic and acousticness > 0.5:
        pts = weights["acoustic"]
        score += pts
        reasons.append(f"acoustic match (+{pts:.1f})")

    # Popularity similarity (Challenge 1)
    pop_sim = 1.0 - abs(popularity - target_popularity) / 100.0
    pts = pop_sim * weights["popularity"]
    score += pts
    reasons.append(f"popularity match ({popularity}/100, +{pts:.2f})")

    # Decade preference (Challenge 1)
    if preferred_decade != 0 and release_decade == preferred_decade:
        pts = weights["decade"]
        score += pts
        reasons.append(f"decade match ({release_decade}s, +{pts:.1f})")

    # Mood-tag partial match (Challenge 1)
    if favorite_mood_tags and mood_tags:
        user_tags = {t.strip().lower() for t in favorite_mood_tags.split(",") if t.strip()}
        song_tags = {t.strip().lower() for t in mood_tags.split(",") if t.strip()}
        matched = user_tags & song_tags
        if matched:
            pts = (len(matched) / max(len(user_tags), 1)) * weights["mood_tags"]
            score += pts
            reasons.append(f"mood tags match ({', '.join(sorted(matched))}, +{pts:.2f})")

    return score, reasons


# ---------------------------------------------------------------------------
# Diversity penalty helpers  (Challenge 3)
# ---------------------------------------------------------------------------

def _apply_diversity_penalty_songs(
    scored: List[Tuple["Song", float]], penalty: float
) -> List[Tuple["Song", float]]:
    """Greedy re-ranking that penalises repeated artists/genres (OOP API)."""
    result: List[Tuple["Song", float]] = []
    remaining = list(scored)
    seen_artists: set = set()
    seen_genres: set = set()

    while remaining:
        best_song, best_score = remaining[0]
        result.append((best_song, best_score))
        seen_artists.add(best_song.artist)
        seen_genres.add(best_song.genre)
        remaining = remaining[1:]

        penalized = []
        for song, score in remaining:
            p = 0.0
            if song.artist in seen_artists:
                p += penalty
            if song.genre in seen_genres:
                p += penalty * 0.5
            penalized.append((song, score - p))
        penalized.sort(key=lambda x: x[1], reverse=True)
        remaining = penalized

    return result


def _apply_diversity_penalty_dicts(
    scored: List[Tuple[Dict, float, str]], penalty: float
) -> List[Tuple[Dict, float, str]]:
    """Greedy re-ranking that penalises repeated artists/genres (functional API)."""
    result: List[Tuple[Dict, float, str]] = []
    remaining = list(scored)
    seen_artists: set = set()
    seen_genres: set = set()

    while remaining:
        best_song, best_score, best_expl = remaining[0]
        result.append((best_song, best_score, best_expl))
        seen_artists.add(best_song.get("artist", ""))
        seen_genres.add(best_song.get("genre", ""))
        remaining = remaining[1:]

        penalized = []
        for song, score, expl in remaining:
            p = 0.0
            if song.get("artist", "") in seen_artists:
                p += penalty
            if song.get("genre", "") in seen_genres:
                p += penalty * 0.5
            note = f" [diversity -{p:.1f}]" if p > 0 else ""
            penalized.append((song, score - p, expl + note))
        penalized.sort(key=lambda x: x[1], reverse=True)
        remaining = penalized

    return result


# ---------------------------------------------------------------------------
# OOP API
# ---------------------------------------------------------------------------

class Recommender:
    """OOP implementation of the recommendation logic. Required by tests/test_recommender.py"""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, diversity_penalty: float = 0.0) -> List[Song]:
        """Return the top k songs ranked by relevance to the user's taste profile."""
        scored = []
        for song in self.songs:
            score, _ = _score_against_profile(
                song.genre, song.mood, song.energy, song.acousticness,
                song.popularity, song.release_decade, song.mood_tags,
                user.favorite_genre, user.favorite_mood,
                user.target_energy, user.likes_acoustic,
                user.target_popularity, user.preferred_decade,
                user.favorite_mood_tags, user.scoring_mode,
            )
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        if diversity_penalty > 0:
            scored = _apply_diversity_penalty_songs(scored, diversity_penalty)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why a song was recommended."""
        _, reasons = _score_against_profile(
            song.genre, song.mood, song.energy, song.acousticness,
            song.popularity, song.release_decade, song.mood_tags,
            user.favorite_genre, user.favorite_mood,
            user.target_energy, user.likes_acoustic,
            user.target_popularity, user.preferred_decade,
            user.favorite_mood_tags, user.scoring_mode,
        )
        return "; ".join(reasons) if reasons else "No strong match found."


# ---------------------------------------------------------------------------
# Functional API
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with numeric fields cast."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            row["popularity"] = int(row.get("popularity") or 50)
            row["release_decade"] = int(row.get("release_decade") or 2020)
            row["mood_tags"] = row.get("mood_tags", "")
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = "") -> Tuple[float, List[str]]:
    """Score a single song dict against user_prefs and return (score, reasons list)."""
    return _score_against_profile(
        song.get("genre", ""),
        song.get("mood", ""),
        song.get("energy", 0.5),
        song.get("acousticness", 0.5),
        song.get("popularity", 50),
        song.get("release_decade", 2020),
        song.get("mood_tags", ""),
        user_prefs.get("genre", ""),
        user_prefs.get("mood", ""),
        user_prefs.get("energy", 0.5),
        user_prefs.get("likes_acoustic", False),
        user_prefs.get("target_popularity", 50),
        user_prefs.get("preferred_decade", 0),
        user_prefs.get("favorite_mood_tags", ""),
        mode or user_prefs.get("scoring_mode", "balanced"),
    )


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    diversity_penalty: float = 0.0,
) -> List[Tuple[Dict, float, str]]:
    """Return the top k (song, score, explanation) tuples sorted by score descending."""
    mode = user_prefs.get("scoring_mode", "balanced")
    scored = []
    for song in songs:
        song_score, reasons = score_song(user_prefs, song, mode)
        explanation = "; ".join(reasons)
        scored.append((song, song_score, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    if diversity_penalty > 0:
        scored = _apply_diversity_penalty_dicts(scored, diversity_penalty)
    return scored[:k]
