# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeCheck 1.0**

---

## 2. Intended Use

VibeCheck is designed to suggest songs that match how a user wants to feel. You tell it your preferred genre, mood, and energy level, and it finds the closest matches in a small catalog of 24 songs. It is built for classroom exploration and learning -- not for real users or production apps. It assumes the user knows what genre and mood they want and can rate their energy preference on a scale from 0 to 1.

**Not intended for:** replacing real music apps, working with large catalogs, or making decisions for actual listeners.

---

## 3. How the Model Works

The system scores every song in the catalog against what the user asked for. It checks three things:

- **Genre** -- does the song match the user's genre? An exact match earns 2 points. A song from a related genre (like indie pop when you asked for pop) earns 1 point.
- **Mood** -- does the song match the user's mood? An exact match earns 1.5 points. A similar mood (like fun when you asked for happy) earns 0.75 points.
- **Energy** -- how close is the song's energy to what the user wants? Very close earns 1 point. Somewhat close earns 0.5 points. Too far off earns nothing.

Every song gets a total score. The system sorts all songs from highest to lowest and returns the top 5. The "Why" line in the output explains exactly which points each song earned.

---

## 4. Data

- 24 songs total in the catalog
- Each song has 11 attributes: title, artist, genre, mood, energy, tempo, valence, danceability, acousticness, and instrumentalness
- 14 different genres are represented (pop, lofi, rock, synthwave, ambient, jazz, and more)
- 13 different moods are represented (happy, chill, intense, dark, reflective, and more)
- The catalog skews toward electronic and indie music. Jazz has only 1 song. Classical has none.
- Songs cluster at either low energy (0.28--0.42) or high energy (0.75--0.93). Very few songs exist in the middle range.

---

## 5. Strengths

- Works well when the user's taste matches what is already in the catalog. Pop, lofi, and rock users all get strong, clear top picks.
- The partial match system (genre and mood families) means the system can still find related songs even when there is no exact match.
- Every recommendation comes with a plain-language explanation of why it was chosen, which makes the system transparent and easy to understand.
- The system never crashes, even when the requested genre is not in the catalog at all.

---

## 6. Limitations and Bias

The biggest weakness is that mid-range energy users get a worse experience. The catalog has almost no songs with energy around 0.5 -- songs are either slow or fast with very little in between. So a user who wants medium energy gets no energy points at all, and their recommendations are decided only by genre and mood. High-energy and low-energy users get the full scoring system. Mid-energy users do not. That is unfair and the system does not warn the user about it.

Genre also has a lot of power. At 2 points it is the highest-weighted attribute, which means a user can get stuck in their genre even when songs from other genres would fit their mood and energy perfectly. The system also cannot detect conflicting preferences -- a user who asks for calm lofi music but high energy gets quiet lofi songs anyway, because genre and mood outweigh energy in the scoring.

---

## 7. Evaluation

Seven profiles were tested in total. Three were normal profiles -- High-Energy Pop, Chill Lofi, and Deep Intense Rock -- to check that the system works when the user's taste matches what is in the catalog. All three gave strong results with clear top picks, which means the basic scoring logic is working.

Four harder profiles were also tested to see where the system breaks down. One asked for calm lofi music but with high energy, which is a contradiction. One asked for jazz, which only has one song in the catalog. One asked for energy 0.5, which barely exists in the catalog. One asked for classical, which is not in the catalog at all.

The most surprising result was the conflict profile. The system recommended slow, quiet lofi songs to a user who asked for high energy -- because genre and mood scored more points than energy. The system had no way to notice the preferences did not make sense together. The jazz test was also interesting: the one jazz song scored very high, but everything after it dropped way down. The classical test showed the system does not crash when a genre is missing -- it just returns weak results without explaining why.

A weight shift experiment was also run where genre points were cut in half and energy points were doubled. The results got worse -- a dark synthwave song tied with a happy pop song for the same user profile, which made no sense. The original weights were restored.

---

## 8. Future Work

- **Add more songs.** Genres like jazz, classical, and folk only have one or zero songs. More catalog variety would make recommendations much more useful for those users.
- **Warn the user when preferences don't match the catalog.** If no song is close to the user's energy target or genre, the system should say so instead of quietly returning weak results.
- **Add a diversity rule.** Right now the top 5 results can all be nearly the same song. A real recommender would make sure the results feel different from each other.

---

## 9. Personal Reflection

Building this showed me that a recommender is only as good as the data behind it. The scoring logic worked exactly as designed, but the results still felt wrong in some cases -- not because the code was broken, but because the catalog was too small or unbalanced. That was unexpected. I assumed getting the math right was the hard part, but choosing what to score and how much weight to give each thing turned out to matter just as much. It also made me think differently about apps like Spotify. When a recommendation feels off, it is probably not a bug -- it is the system making a trade-off between different signals, just like VibeCheck does.
