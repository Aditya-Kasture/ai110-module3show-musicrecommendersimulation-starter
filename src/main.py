"""
Command line runner for the Music Recommender Simulation.

Runs six user profiles (three standard + three edge-case/adversarial),
a weight-shift experiment comparing balanced vs energy-focused scoring,
and a diversity-penalty demo. Output is displayed as a formatted table.
"""

try:
    from recommender import load_songs, recommend_songs, SCORING_MODES
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs, SCORING_MODES

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False


# ---------------------------------------------------------------------------
# User profiles  (Phase 4 Step 1)
# ---------------------------------------------------------------------------

PROFILES = {
    # --- Standard profiles ---
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.85,
        "likes_acoustic": False, "target_popularity": 80,
        "scoring_mode": "balanced",
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.38,
        "likes_acoustic": True, "target_popularity": 60,
        "preferred_decade": 2020, "scoring_mode": "mood_first",
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.92,
        "likes_acoustic": False, "target_popularity": 65,
        "scoring_mode": "genre_first",
    },
    # --- Edge-case / adversarial profiles (Phase 4 Step 1) ---
    "Conflicting: High Energy + Chill Mood": {
        # Tests whether energy or mood wins when they point in opposite directions
        "genre": "ambient", "mood": "chill", "energy": 0.90,
        "likes_acoustic": False, "scoring_mode": "energy_focused",
    },
    "Niche Folk Listener": {
        # Only one folk song exists - tests catalog coverage failure
        "genre": "folk", "mood": "relaxed", "energy": 0.32,
        "likes_acoustic": True, "target_popularity": 40,
        "preferred_decade": 2010, "scoring_mode": "mood_first",
    },
    "Mood-Tag Hunter (nostalgic + euphoric)": {
        # Relies entirely on the new mood_tags feature
        "genre": "pop", "mood": "happy", "energy": 0.80,
        "likes_acoustic": False,
        "favorite_mood_tags": "nostalgic,euphoric",
        "scoring_mode": "balanced",
    },
}

# Phase 4 Step 3 - weight-shift experiment
EXPERIMENT_PROFILES = {
    "Experiment A - Balanced (genre w=2.0, energy w=1.0)": {
        "genre": "pop", "mood": "happy", "energy": 0.80,
        "likes_acoustic": False, "scoring_mode": "balanced",
    },
    "Experiment B - Energy-Focused (energy w=3.0, genre w=0.5)": {
        "genre": "pop", "mood": "happy", "energy": 0.80,
        "likes_acoustic": False, "scoring_mode": "energy_focused",
    },
}


# ---------------------------------------------------------------------------
# Display helpers  (Challenge 4: Visual Summary Table)
# ---------------------------------------------------------------------------

def _ascii_table(rows: list, headers: list) -> str:
    """Fallback ASCII table used when tabulate is not installed."""
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    fmt = "| " + " | ".join(f"{{:<{w}}}" for w in col_widths) + " |"
    lines = [sep, fmt.format(*[str(h) for h in headers]), sep]
    for row in rows:
        lines.append(fmt.format(*[str(c) for c in row]))
    lines.append(sep)
    return "\n".join(lines)


def print_recommendations(label: str, recs: list, diversity: bool = False) -> None:
    """Print a formatted results table for one profile."""
    print(f"\n{'=' * 62}")
    print(f"  {label}")
    if diversity:
        print("  [diversity penalty = 0.5 applied]")
    print(f"{'=' * 62}")

    rows = []
    for rank, (song, score, explanation) in enumerate(recs, 1):
        title = song["title"][:24]
        genre = song["genre"][:12]
        score_str = f"{score:.2f}"
        top_reason = explanation.split(";")[0].strip()[:36]
        rows.append((rank, title, genre, score_str, top_reason))

    headers = ["#", "Title", "Genre", "Score", "Top Reason"]
    if _HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        print(_ascii_table(rows, headers))


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")
    print(f"Available scoring modes: {', '.join(SCORING_MODES)}\n")

    # --- Standard profiles ---
    print("=" * 62)
    print("  STANDARD PROFILES")
    print("=" * 62)
    standard = {k: v for k, v in PROFILES.items()
                if not k.startswith("Conflict") and not k.startswith("Niche") and not k.startswith("Mood-Tag")}
    for label, prefs in standard.items():
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(label, recs)

    # --- Edge-case / adversarial profiles ---
    print("\n" + "=" * 62)
    print("  EDGE-CASE / ADVERSARIAL PROFILES")
    print("=" * 62)
    edge = {k: v for k, v in PROFILES.items()
            if k.startswith("Conflict") or k.startswith("Niche") or k.startswith("Mood-Tag")}
    for label, prefs in edge.items():
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(label, recs)

    # --- Weight-shift experiment (Phase 4 Step 3) ---
    print("\n" + "=" * 62)
    print("  WEIGHT-SHIFT EXPERIMENT")
    print("=" * 62)
    for label, prefs in EXPERIMENT_PROFILES.items():
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(label, recs)

    # --- Diversity penalty demo (Challenge 3) ---
    print("\n" + "=" * 62)
    print("  DIVERSITY PENALTY DEMO  (High-Energy Pop)")
    print("=" * 62)
    recs_no_div = recommend_songs(PROFILES["High-Energy Pop"], songs, k=5)
    recs_div    = recommend_songs(PROFILES["High-Energy Pop"], songs, k=5, diversity_penalty=0.5)
    print_recommendations("Without diversity penalty", recs_no_div)
    print_recommendations("With diversity penalty (0.5)", recs_div, diversity=True)


if __name__ == "__main__":
    main()
