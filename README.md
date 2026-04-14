# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This recommender does not just match songs by genre or mood label. It tries to understand what kind of experience a listener is looking for — how they want to feel, what kind of atmosphere they want to be in, and what the music should do for them emotionally. A song is scored based on how well it creates that experience, not just whether it fits a category. The system looks at things like emotional weight, how immersive the sound is, and whether the song builds over time before deciding what to recommend.

---

## How The System Works

Real-world recommenders like Spotify figure out what to play next by either looking at what similar users enjoyed (collaborative filtering) or by comparing the qualities of songs directly (content-based filtering). This simulation uses content-based filtering — it looks at each song's attributes and matches them to what the user is looking for. My version prioritizes how a song feels over time rather than just its genre label, focusing on emotional weight, atmosphere, and how immersive the listening experience is.

**Song features used:**
- `genre` — musical style
- `mood` — emotional label
- `energy` — intensity from 0.0 to 1.0
- `valence` — brightness vs darkness from 0.0 to 1.0
- `acousticness` — acoustic vs electronic feel from 0.0 to 1.0
- `danceability` — movement suitability from 0.0 to 1.0
- `tempo_bpm` — speed in beats per minute

**UserProfile features used:**
- `favorite_genre` — the genre the user prefers
- `favorite_mood` — the mood they are looking for
- `target_energy` — their preferred energy level from 0.0 to 1.0
- `target_valence` — how dark or bright they want the music from 0.0 (dark) to 1.0 (bright)
- `likes_acoustic` — whether they prefer acoustic or electronic sound
- `emotional_purpose` — why they are listening: release, escape, reflection, or focus
- `listening_mode` — how they are listening: focused or immersive
- `environment_fit` — the context they are listening in: night drive, alone thinking, background, or workout
- `intensity_type` — the kind of intensity they want: aggressive, atmospheric, aesthetic, emotional, or hybrid

**Algorithm Recipe:**

Each song is scored against the user profile in two layers. The final score determines its rank in the playlist.

*Base layer — always applied:*

| Attribute | Exact match | Partial match (same family) |
|---|---|---|
| Genre | +2.0 | +1.0 |
| Mood | +1.5 | +0.75 |
| Energy | +1.0 (diff ≤ 0.10) | +0.5 (diff ≤ 0.25) |
| Valence | +1.0 (diff ≤ 0.10) | +0.5 (diff ≤ 0.25) |
| Acoustic preference | +0.5 | — |

Genre family examples: lofi, ambient, and dream pop are in the same family. Rock, metalcore, and post-metal are in the same family. Mood family examples: happy and fun are positive. Chill, relaxed, and focused are calm. Moody, dark, emotional, and reflective are dark.

*Context layer — only fires when the user sets the optional profile fields:*

| Field | What it rewards | Max points |
|---|---|---|
| `emotional_purpose` | Instrumentalness for focus; energy + danceability for release; acousticness for escape; quiet tone for reflection | +1.0 |
| `listening_mode` | High instrumentalness + acousticness for immersive; instrumentalness alone for focused | +0.75 |
| `environment_fit` | Energy + tempo for workout; rhythm for night drive; quiet acoustics for alone thinking; instrumentalness for background | +1.0 |
| `intensity_type` | Energy + low valence for aggressive; acousticness for atmospheric; danceability + valence for aesthetic; dark mood for emotional | +0.75 |

Maximum possible score: approximately 10.0. Most songs will score between 2 and 6. A song that only matches genre and mood will score at most 3.5. A song that also fits the user's context can reach 7 or higher.

**Potential Biases:**

- The system may over-reward genre matches and bury songs that fit the user's mood and context perfectly but belong to an unfamiliar genre. A user who says they want focus music might miss *Time* by Hans Zimmer (soundtrack) if they only listed lofi as their genre.
- Genre and mood families reflect a specific cultural grouping. Placing metalcore and post-metal in the same family, or happy and fun in the same family, is a judgment call that may not match every listener's view.
- The context layer only activates when optional fields are filled in. A user who only sets genre and mood gets a shallower score, which means two very different songs could tie even if one is clearly a better fit.
- There is no diversity mechanism. The top five results could all be very similar songs if they share the same genre and mood. A real recommender would penalize repetition.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

The biggest learning moment for me was realizing that getting the code to work is only half the problem. I spent a lot of time thinking about the scoring logic, but when I actually ran it, the results sometimes felt wrong even though the math was correct. That taught me that the data and the weights matter just as much as the code itself. Using AI tools helped me move faster, especially when I was figuring out how to structure the scoring system and what the algorithm recipe should look like. But I still had to double-check things.What surprised me most was how a system with only three rules -- genre, mood, and energy -- could actually feel like it was making real recommendations. When Sunrise City came up as the top result for the pop/happy profile, it genuinely felt right. But then when I ran the conflict profile and got quiet lofi songs for someone who asked for high energy, it reminded me that the system has no common sense. It just follows the math.
