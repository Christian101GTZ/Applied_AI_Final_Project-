# Reflection: Profile Comparison Notes

---

## Pair 1: High-Energy Pop vs Deep Intense Rock

Both profiles asked for high energy music but in different genres and moods. The pop profile returned upbeat, feel-good songs like Sunrise City and Blinding Lights. The rock profile returned heavy, intense songs like Storm Runner and Doomsday. Even though both profiles wanted similar energy levels, the results felt completely different. This shows that energy alone does not tell the whole story -- genre and mood are what actually shape what kind of song you get.

---

## Pair 2: Chill Lofi vs Conflict (Calm Mood + High Energy)

These two profiles both asked for lofi music with a calm mood, but one asked for low energy (0.40) and the other asked for high energy (0.90). Surprisingly, both profiles returned the exact same top songs. That happened because genre and mood earned more points than energy, so the energy difference did not change anything. The problem is that no lofi song in the catalog has high energy -- so the high energy request was completely ignored. The system should have flagged this as a conflict, but instead it quietly skipped it and gave the same results anyway.

---

## Pair 3: Rare Genre (Jazz) vs Genre Not in Catalog (Classical)

The jazz profile had one perfect match in the catalog -- Coffee Shop Stories -- which scored very high. But after that one song, the next four results dropped way down in score because there are no other jazz songs. The classical profile had zero matches at all, so the system just picked songs with similar energy and returned five unrelated results all tied at the same low score. In both cases the system never told the user "we don't have much of what you're looking for." That would have been more helpful than quietly returning weak results.

---

## Pair 4: High-Energy Pop vs No-Mans-Land Energy (Pop, Happy, Energy 0.5)

These two profiles were almost identical except one asked for energy 0.92 and the other asked for energy 0.50. The high energy profile scored energy points on most pop songs. The 0.50 energy profile scored almost no energy points because the catalog has very few songs near 0.50 -- most songs are either slow (lofi) or fast (pop and rock) with almost nothing in between. So the same songs ended up at the top, just with lower scores. This means two users with the same genre and mood but different energy preferences got the same recommendations, which defeats the purpose of asking for energy at all.

---

## Overall Takeaway

The recommender works well when the user's preferences match what is already in the catalog. When they don't -- because the genre is rare, the energy is in a gap, or the preferences conflict -- the system still returns results without explaining why they might not be a good fit. The biggest lesson is that a recommender is only as useful as the data behind it.
