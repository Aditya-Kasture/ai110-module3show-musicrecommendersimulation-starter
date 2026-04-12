# Profile Comparisons - VibeFinder Evaluation Notes

This file documents observations and comparisons across the user profiles tested during Phase 4.

---

## Pair 1: High-Energy Pop vs Chill Lofi

**High-Energy Pop** (pop / happy / energy 0.85, mode: balanced):
```
1. Sunrise City   - pop    - 4.26
2. Gym Hero       - pop    - 3.21
3. Neon Blossom   - k-pop  - 2.27
4. Rooftop Lights - indie  - 2.17
5. Golden Hour    - r&b    - 2.15
```

**Chill Lofi** (lofi / chill / energy 0.38, mode: mood_first):
```
1. Library Rain        - lofi    - 5.18
2. Midnight Coding     - lofi    - 5.17
3. Spacewalk Thoughts  - ambient - 4.10
4. Island Groove       - reggae  - 4.01
5. Focus Flow          - lofi    - 2.18
```

**What changed and why:** The High-Energy Pop list is dominated by pop songs because genre earns +2.0 in balanced mode. The Chill Lofi list is dominated by mood matches because mood_first mode gives mood a +3.0 weight, larger than the +1.0 genre weight. This is why Spacewalk Thoughts (ambient, not lofi) and Island Groove (reggae, not lofi) appear at positions 3 and 4: they match the "chill" mood better than the third lofi song (Focus Flow, which is "focused," not "chill").

**Lesson:** Scoring mode has a larger effect on list composition than any individual user preference. The same catalog produces very different results just by changing the weight preset.

---

## Pair 2: High-Energy Pop vs Conflicting (High Energy + Chill Mood)

**High-Energy Pop** (pop / happy / energy 0.85, mode: balanced) - top genre: pop
**Conflicting** (ambient / chill / energy 0.90, mode: energy_focused) - top genres: rock, hip-hop, pop, electronic, metal

**What changed and why:** In energy_focused mode, the energy weight is 3.0 and genre is only 0.5. The "conflicting" user wants high energy (0.9) but a chill mood. Because energy is 6× more influential than genre in this mode, the system returns the five highest-energy songs in the entire catalog regardless of mood or genre. The user asked for "chill" but gets Storm Runner (rock, intense) at the top.

**Lesson:** When two preferences conflict and the scoring mode heavily favors one dimension, the system cannot flag the problem; it silently picks the dominant signal. A real system would need to detect and explain this tension to the user.

---

## Pair 3: Weight Experiment A (Balanced) vs Experiment B (Energy-Focused)

Same user: pop / happy / energy 0.80.

**Balanced** (genre w=2.0, energy w=1.0):
```
1. Sunrise City    - pop       - 4.20
2. Gym Hero        - pop       - 3.06
3. Rooftop Lights  - indie pop - 2.21
4. Golden Hour     - r&b       - 2.15
5. Neon Blossom    - k-pop     - 2.15
```

**Energy-Focused** (energy w=3.0, genre w=0.5):
```
1. Sunrise City    - pop       - 4.08
2. Rooftop Lights  - indie pop - 3.54
3. Neon Blossom    - k-pop     - 3.50
4. Golden Hour     - r&b       - 3.41
5. Gym Hero        - pop       - 3.24
```

**What changed and why:** Gym Hero (energy 0.93) drops from #2 to #5 even though it matches the user's genre. Why? Its energy is 0.93, which is 0.13 away from the user's target of 0.80. In energy_focused mode that 0.13 gap is penalised by a factor of 3.0, costing it 0.39 points. Meanwhile Rooftop Lights has energy 0.76, much closer to 0.80, and rises to #2. The genre label ("indie pop" vs "pop") barely matters in energy_focused mode.

**Lesson:** The weight experiment is the clearest demonstration that changing one number in the design silently reorders the entire recommendation list. "Gym Hero is #2 for a pop fan" is not a property of the music; it is a property of the weight preset.

---

## Pair 4: Without Diversity Penalty vs With Diversity Penalty (High-Energy Pop)

**Without penalty:**
```
1. Sunrise City    - pop       - 4.26
2. Gym Hero        - pop       - 3.21
3. Neon Blossom    - k-pop     - 2.27
4. Rooftop Lights  - indie pop - 2.17
5. Golden Hour     - r&b       - 2.15
```

**With penalty (0.5):**
```
1. Sunrise City    - pop       - 4.26
2. Gym Hero        - pop       - 2.96  (genre penalty -0.25 applied)
3. Neon Blossom    - k-pop     - 2.27
4. Rooftop Lights  - indie pop - 2.17
5. Golden Hour     - r&b       - 2.15
```

**What changed and why:** Only Gym Hero's score changed (from 3.21 to 2.96) because it shares the "pop" genre with Sunrise City (already selected at #1). The penalty of 0.5 * 0.5 = 0.25 was subtracted. However, the ranking order didn't change because Gym Hero's adjusted score (2.96) is still higher than Neon Blossom (2.27).

**Lesson:** At 18 songs the diversity penalty mostly changes scores without changing the ranking, because the high-scoring songs are already spread across different genres and artists. The penalty would matter more in a larger catalog where many similar songs cluster at the top.

---

## Overall Summary

The most important insight across all four comparisons: **the scoring mode (weight preset) has a larger effect on the output than any individual song attribute or user preference.** A designer who quietly sets genre_weight=4.0 is making a choice that affects every user, on every session, forever, and that choice is invisible to the user.

Plain-language explanation for a non-programmer:
> "Gym Hero keeps showing up for 'Happy Pop' users because the scoring rule gives a big bonus (2 full points) just for matching the genre label 'pop.' No other factor comes close to that size. So if you're a pop fan, the pop songs will always crowd the top of the list, even if a better-fitting song from a slightly different genre is right there in the catalog."
