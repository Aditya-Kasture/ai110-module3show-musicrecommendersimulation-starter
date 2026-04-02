# Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender simulation.

---

## 2. Goal / Task

VibeFinder takes a user's stated preferences (favorite genre, mood, energy level, and optional vibe tags) and returns the top 5 most relevant songs from an 18-song catalog, along with a plain-language explanation for each recommendation. The goal is to simulate how real streaming platforms match song attributes to listener taste profiles.

---

## 3. Data Used

- **Catalog size:** 18 songs (10 starter + 8 added)
- **Genres:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, electronic, country, hip-hop, metal, reggae, k-pop, folk
- **Moods:** happy, chill, intense, relaxed, moody, focused, hype
- **Numerical features:** energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1), popularity (0–100)
- **New features (Challenge 1):** release_decade, mood_tags (comma-separated vibe descriptors)

**Limits:** The catalog was manually constructed for classroom use. It reflects Western popular music styles. Genres like classical, Afrobeats, Bollywood, and Latin are absent. No real user listening data was used.

---

## 4. Algorithm Summary

For every song in the catalog, VibeFinder calculates a score by checking seven things:

1. **Genre match** — if the song's genre matches the user's favorite, it earns the biggest bonus (the weight depends on the chosen scoring mode).
2. **Mood match** — if the song's mood matches, it earns a medium bonus.
3. **Energy closeness** — songs whose energy level is close to the user's target earn up to the full energy weight; songs far away earn close to zero.
4. **Acoustic preference** — if the user likes acoustic music and the song is highly acoustic, a small bonus is added.
5. **Popularity similarity** — songs whose popularity score (0–100) is close to the user's target earn a small bonus.
6. **Decade preference** — if the user specifies an era, songs from that decade get a small bonus.
7. **Mood-tag matching** — if the user specifies vibe tags like "euphoric" or "nostalgic," songs with overlapping tags earn a proportional bonus.

After all songs are scored, they are sorted from highest to lowest. The top 5 are returned. A diversity penalty can optionally reduce scores for songs that share an artist or genre with a song already selected.

Four scoring mode presets are available — **balanced**, **genre_first**, **mood_first**, and **energy_focused** — each shifting the relative importance of the features above.

---

## 5. Observed Behavior / Biases

- **Genre dominance creates a filter bubble.** In balanced mode, a genre match is worth twice a mood match. In practice, the top 5 results almost always come from the user's preferred genre—even when cross-genre songs are a better overall fit. This is the most significant bias in the system.

- **Exact string matching is brittle.** "indie pop" and "pop" score zero genre overlap. A pop fan will never receive Rooftop Lights (indie pop) through genre matching alone, only through mood/energy spillover.

- **Conflicting preferences produce silently wrong results.** A user who wants chill mood but very high energy will receive intense rock and hip-hop tracks. The system adds up numbers without flagging that the inputs are contradictory.

- **Catalog sparsity amplifies errors.** The "Niche Folk Listener" profile gets only one true genre match (Desert Wind). After that, results fall back to mood similarity across jazz, country, and ambient—plausible but misleading.

- **The diversity penalty is cosmetic at this scale.** With 18 songs, the top-5 genre distribution rarely changes after applying the penalty; it mainly reduces the scores of a second song from the same genre.

---

## 6. Evaluation Process

Six user profiles were tested, covering three standard use cases and three adversarial/edge cases:

| Profile | Mode | Key Finding |
|---|---|---|
| High-Energy Pop | balanced | Sunrise City and Gym Hero dominate; genre weight drives everything |
| Chill Lofi | mood_first | Library Rain and Midnight Coding top the list; mood_first mode amplifies chill-mood ambient songs into top 4 |
| Deep Intense Rock | genre_first | Storm Runner scores 4.98; the catalog has only one rock song, so positions 2–5 are all wrong-genre mood matches |
| Conflicting (high-energy + chill mood) | energy_focused | Zero ambient/chill songs appear; energy weight wins completely |
| Niche Folk | mood_first | One true match (Desert Wind), then jazz/country mood fallbacks |
| Weight Experiment | balanced vs energy_focused | Switching modes moves Gym Hero from #2 to #5 for the same pop/happy/0.8 user |

The automated unit tests in `tests/test_recommender.py` confirm that the pop/happy/0.8 song consistently outscores the lofi/chill song for a matching user profile.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Classroom simulation to understand content-based filtering
- Learning tool for exploring how scoring weights affect outputs
- Foundation for studying AI bias and fairness in recommendations

**Not intended for:**
- Real product deployment or actual users
- Making commercial music recommendations
- Any context where biased outputs could affect someone's access to content or livelihood

---

## 8. Ideas for Improvement

1. **Score more features continuously.** Valence, danceability, and tempo are loaded but unused. Adding similarity scores for these would give the system a richer picture of musical texture.
2. **Soft genre matching.** Group related genres (pop, indie pop, k-pop) into a parent category so a partial genre match earns partial credit rather than zero.
3. **Conflict detection.** Before scoring, check if the user's energy and mood preferences point in opposite directions (e.g., energy > 0.8 + mood = "chill") and surface a warning.
4. **Diversity-aware re-ranking.** Enforce a hard rule: no more than two songs from the same genre in the top 5, regardless of scores.
5. **Hybrid scoring.** Combine content-based scoring with a simple collaborative signal derived from user skip/like history.

---

## 9. Personal Reflection

**Biggest learning moment:** Seeing the weight-shift experiment run. Changing the energy weight from 1.0 to 3.0 moved Gym Hero from #2 to #5 for the same user. That one number—quietly set during the design phase—shapes every recommendation the system ever makes. Real platforms make thousands of decisions like that, and they are rarely examined or explained.

**How AI tools helped:** Using AI tools to research scoring strategies and sanity-check the logic helped surface the exact-string-matching problem early and structure the function cleanly. But no AI tool could decide *which* design choices were right for the project goals—that required thinking about what a "good" recommendation means and for whom. The tool is most useful when you already understand the problem well enough to evaluate its suggestions critically.

**What surprised me about simple algorithms:** The conflicting-preferences profile was the most revealing. A user who wants chill mood but high energy receives five intense rock and hip-hop tracks, zero ambient, zero chill. The system has no way to negotiate between contradictory signals—it just adds the numbers and the louder weight wins. Spotify's magic partly comes from having millions of songs: with enough catalog depth, even a naive scoring rule will surface something great. At 18 songs, every flaw is immediately visible.

**What I would try next:** Add a second user profile comparison mode—given two users, find the songs that score in the top 10 for both simultaneously. This "group recommendation" problem reveals another layer of bias: whose preferences get compromised when they conflict.
