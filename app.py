import os
import json
import logging
import time
from typing import Optional
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.recommender import load_songs, score_song, recommend_songs, GENRE_FAMILIES

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("recommender.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

CATALOG_PATH = "data/songs.csv"
MODEL = "gemini-2.5-flash"

GENRES = list(GENRE_FAMILIES.keys())
MOODS = [
    "happy", "fun", "nostalgic", "hopeful", "romantic",
    "chill", "relaxed", "focused", "peaceful",
    "sad", "melancholic", "emotional", "reflective", "moody", "dark",
    "intense", "aggressive", "angry", "epic",
]
LYRICAL_THEMES = [
    "none", "love", "loss", "struggle", "motivation",
    "reflection", "nostalgia", "darkness", "celebration", "abstract",
]


# ── Catalog ───────────────────────────────────────────────────────────────────

@st.cache_data
def load_catalog():
    try:
        songs = load_songs(CATALOG_PATH)
        logger.info(f"Catalog loaded: {len(songs)} songs")
        return songs
    except Exception as e:
        logger.error(f"Failed to load catalog: {e}")
        return []


# ── Helpers ───────────────────────────────────────────────────────────────────

def youtube_url(song: dict) -> str:
    if song.get("youtube_id"):
        return f"https://youtube.com/watch?v={song['youtube_id']}"
    query = f"{song['title']} {song['artist']}".replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={query}"


def safe_json(text: str) -> Optional[dict]:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end]) if start != -1 else None
    except Exception:
        return None


def call_with_retry(fn, retries=3, base_wait=10):
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = base_wait * (attempt + 1)
                logger.warning(f"Rate limited — waiting {wait}s before retry {attempt + 1}")
                time.sleep(wait)
            else:
                raise


def update_taste_profile(profile: dict, parsed: dict) -> dict:
    if parsed.get("genre"):
        profile["genres"].append(parsed["genre"])
    if parsed.get("mood"):
        profile["moods"].append(parsed["mood"])
    if parsed.get("energy") is not None:
        profile["energies"].append(float(parsed["energy"]))
    profile["request_count"] += 1
    return profile


def get_feedback_summary(feedback: dict, catalog: list) -> str:
    liked_ids = {sid for sid, f in feedback.items() if f == "liked"}
    if not liked_ids:
        return ""
    liked = [s for s in catalog if s["id"] in liked_ids]
    if not liked:
        return ""
    genres = list({s["genre"] for s in liked})
    moods = list({s["mood"] for s in liked})
    avg_energy = sum(s["energy"] for s in liked) / len(liked)
    return (
        f"Songs the user explicitly liked this session: "
        f"genres={genres}, moods={moods}, avg energy={avg_energy:.2f}. "
        f"Lean toward these qualities when the current request allows it."
    )


# ── Gemini: Parse Intent ──────────────────────────────────────────────────────

def parse_intent(client: genai.Client, user_input: str, history: list, taste_profile: dict = None, feedback_summary: str = "") -> dict:
    profile_context = ""
    if taste_profile and taste_profile.get("request_count", 0) > 0:
        recent_genres = list(dict.fromkeys(taste_profile["genres"][-5:]))
        recent_moods  = list(dict.fromkeys(taste_profile["moods"][-5:]))
        avg_energy    = sum(taste_profile["energies"]) / len(taste_profile["energies"]) if taste_profile["energies"] else None
        profile_context = (
            f"\nUser session profile (built from {taste_profile['request_count']} previous requests):\n"
            f"- Genres they've gravitated toward: {', '.join(recent_genres) if recent_genres else 'varied'}\n"
            f"- Moods they've preferred: {', '.join(recent_moods) if recent_moods else 'varied'}\n"
            + (f"- Average energy they've requested: {avg_energy:.2f}\n" if avg_energy is not None else "")
            + "Use this to fill in gaps when the current request is vague.\n"
        )

    feedback_context = f"\n{feedback_summary}\n" if feedback_summary else ""

    system = f"""You are a music preference interpreter for VibeCheck, a music recommender.

Convert the user's natural language request into structured preferences.

Available genres: {", ".join(GENRES)}
Available moods: {", ".join(MOODS)}
Available lyrical themes: {", ".join(LYRICAL_THEMES)}

Energy: float 0.0 (silent/slow) to 1.0 (maximum intensity).
Lyrical intensity: float 0.0 (instrumental) to 1.0 (extremely heavy/emotional lyrics).

CRITICAL RULES — read carefully:
- Set needs_clarification to FALSE whenever the user mentions ANY of: a mood word, a genre word, an activity, an energy descriptor, a feeling, or a listening context. ONE signal is enough to proceed.
- NEVER ask for clarification if the user said "chill", "slow", "fast", "sad", "happy", "relaxing", "energetic", "dark", "calm", "study", "gym", "sleep", "drive", or any similar descriptor. These are all sufficient to recommend.
- Only set needs_clarification to TRUE if the message is completely uninterpretable as a music request (e.g. "I don't know", "anything", "help").
- If clarification IS needed, ask ONE short friendly question in plain everyday language — no music jargon. Ask about how they're feeling or what they want the music to do for them (e.g. "Are you looking for something calm or something upbeat?"). Never use words like "mood", "genre", "energy", or "style" in the question.
- USE conversation history. If the user answered a previous clarification question, combine their answer with earlier context before parsing.

Direct mappings — always apply these without asking:
- "chill", "chill music", "relaxing" → mood: chill, energy: ~0.38
- "slow" → energy: ~0.28
- "fast", "hype", "pump up" → energy: ~0.88, mood: intense
- "sad" → mood: sad, energy: ~0.30
- "happy", "feel good" → mood: happy, energy: ~0.78
- "study", "focus", "work" → mood: focused, genre: lofi, energy: ~0.38
- "sleep", "bedtime" → mood: peaceful, energy: ~0.18
- "gym", "workout" → mood: intense, energy: ~0.90
- "late night drive" → genre: synthwave, mood: dark, energy: ~0.72
- "sad but beautiful" → mood: melancholic, genre: indie folk
- "intense lyrics" → lyrical_intensity: ~0.88
- "no lyrics", "instrumental" → lyrical_intensity: 0.0, lyrical_theme: none
- "cooking", "dinner", "dinner party" → mood: happy, energy: ~0.62
- "morning", "wake up", "getting ready" → mood: hopeful, energy: ~0.65
- "party", "pregame", "going out" → mood: fun, energy: ~0.85
- "heartbreak", "breakup", "miss someone" → mood: sad, energy: ~0.30, lyrical_theme: loss
- "road trip", "long drive" → mood: nostalgic, energy: ~0.70
- "meditation", "yoga", "breathing" → mood: peaceful, energy: ~0.18
- "running", "jogging" → mood: intense, energy: ~0.85
- "rainy day", "cozy night in" → mood: melancholic, genre: indie folk, energy: ~0.35
- "angry", "need to vent", "frustrated" → mood: aggressive, energy: ~0.85
- "date night", "romantic evening" → mood: romantic, energy: ~0.45
- "can't sleep", "3am", "late night" → mood: melancholic, energy: ~0.28
- "afrobeats", "african music" → genre: afrobeats
- "k-pop", "kpop", "korean pop" → genre: k-pop
- "city pop", "japanese pop", "80s japanese" → genre: city pop
- "bossa nova", "brazilian jazz" → genre: bossa nova
- "trip-hop", "portishead vibes", "massive attack vibes" → genre: trip-hop
{profile_context}{feedback_context}
Return only valid JSON:
{{
  "genre": string or null,
  "mood": string or null,
  "energy": float or null,
  "lyrical_intensity": float or null,
  "lyrical_theme": string or null,
  "needs_clarification": boolean,
  "clarification_question": string or null,
  "reasoning": string
}}"""

    gemini_history = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])]
        )
        for m in history
    ]

    try:
        def _call():
            chat = client.chats.create(
                model=MODEL,
                config=types.GenerateContentConfig(system_instruction=system),
                history=gemini_history,
            )
            return chat.send_message(user_input)

        response = call_with_retry(_call)
        raw = response.text
        logger.info(f"Parse intent raw: {raw}")
        parsed = safe_json(raw)
        if not parsed:
            logger.warning("parse_intent returned invalid JSON — using fallback")
            return {"needs_clarification": True, "clarification_question": "I want to find the right songs for you! What kind of mood are you in — something calm, upbeat, sad, or something else?"}
        return parsed
    except Exception as e:
        logger.error(f"parse_intent error: {e}")
        return {"needs_clarification": True, "clarification_question": "I want to find the right songs for you! What kind of mood are you in — something calm, upbeat, sad, or something else?"}


# ── Gemini: Evaluate Results ──────────────────────────────────────────────────

def evaluate_results(client: genai.Client, user_input: str, parsed: dict, results: list) -> dict:
    song_list = "\n".join(
        f"{i+1}. {r[0]['title']} — {r[0]['artist']} | genre: {r[0]['genre']} | mood: {r[0]['mood']} | energy: {r[0]['energy']} | score: {r[1]:.2f}"
        for i, r in enumerate(results)
    )
    prompt = f"""User requested: "{user_input}"
Parsed preferences: {json.dumps(parsed, indent=2)}

Top recommendations from the scoring algorithm:
{song_list}

Evaluate whether these recommendations genuinely fit the request. Check:
1. Do the songs fit what the user actually asked for?
2. Is there a contradiction between the preferences and the results?
3. Do the 5 songs work together as a cohesive playlist?
4. Overall confidence: high, medium, or low?

Return only valid JSON:
{{
  "confidence": "high" | "medium" | "low",
  "verdict": "one or two sentence summary",
  "contradiction_detected": boolean,
  "contradiction_note": string or null,
  "cohesion_score": "strong" | "moderate" | "weak",
  "flags": []
}}"""

    try:
        response = call_with_retry(lambda: client.models.generate_content(model=MODEL, contents=prompt))
        raw = response.text
        logger.info(f"Evaluation raw: {raw}")
        result = safe_json(raw)
        if not result:
            logger.warning("evaluate_results returned invalid JSON")
            return {"confidence": "medium", "verdict": "Results returned.", "contradiction_detected": False, "cohesion_score": "moderate", "flags": []}
        return result
    except Exception as e:
        logger.error(f"evaluate_results error: {e}")
        return {"confidence": "medium", "verdict": "Evaluation unavailable.", "contradiction_detected": False, "cohesion_score": "moderate", "flags": []}


# ── Gemini: Generate Explanations ─────────────────────────────────────────────

def generate_explanations(client: genai.Client, user_input: str, parsed: dict, results: list) -> list:
    song_list = "\n".join(
        f"{i+1}. {r[0]['title']} — {r[0]['artist']} | genre: {r[0]['genre']} | mood: {r[0]['mood']} | energy: {r[0]['energy']} | lyrical theme: {r[0].get('lyrical_theme','none')}"
        for i, r in enumerate(results)
    )
    prompt = f"""User requested: "{user_input}"
Parsed preferences: {json.dumps(parsed, indent=2)}

Songs to explain:
{song_list}

Write one natural, conversational sentence per song explaining why it fits the user's request.
Be specific about the song's qualities — not just the matching labels.
Do not start every sentence with "This song".
Mirror the user's tone and language exactly — if they were casual, be casual; if they were poetic or emotional, match that energy; if they used slang or a specific vibe ("hits different", "banger", "vibe"), use that same language back. Reference their exact words when it feels natural.

Return only a valid JSON array of exactly {len(results)} strings, one per song in order:
["explanation for song 1", "explanation for song 2", ...]"""

    try:
        response = call_with_retry(lambda: client.models.generate_content(model=MODEL, contents=prompt))
        raw = response.text
        logger.info(f"Explanations raw: {raw}")
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start != -1:
            explanations = json.loads(raw[start:end])
            if isinstance(explanations, list) and len(explanations) == len(results):
                return explanations
        logger.warning("generate_explanations returned unexpected format")
    except Exception as e:
        logger.error(f"generate_explanations error: {e}")

    return [f"Matches your request for {parsed.get('mood', 'this vibe')}." for _ in results]


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(client: genai.Client, catalog, user_input, history, taste_profile: dict = None, song_feedback: dict = None):
    logger.info(f"Pipeline started — input: {user_input!r}")

    feedback_summary = get_feedback_summary(song_feedback or {}, catalog)
    parsed = parse_intent(client, user_input, history, taste_profile, feedback_summary)

    if parsed.get("needs_clarification"):
        logger.info("Clarification needed")
        return {"type": "clarification", "question": parsed.get("clarification_question", "Could you tell me more?")}

    user_prefs = {k: parsed[k] for k in ("genre", "mood", "energy", "lyrical_intensity", "lyrical_theme") if parsed.get(k) is not None}
    logger.info(f"Parsed preferences: {user_prefs}")

    all_results = recommend_songs(user_prefs, catalog, k=10)
    results = all_results[:5]
    pool = all_results[5:]
    logger.info(f"Scored {len(catalog)} songs, returning top {len(results)} with {len(pool)} in reserve pool")

    evaluation = evaluate_results(client, user_input, parsed, results)
    logger.info(f"Evaluation confidence: {evaluation.get('confidence')}")

    if evaluation.get("confidence") == "low":
        logger.info("Low confidence — retrying with relaxed preferences")
        relaxed = {k: v for k, v in user_prefs.items() if k != "energy"}
        all_results = recommend_songs(relaxed, catalog, k=10)
        results = all_results[:5]
        pool = all_results[5:]
        evaluation = evaluate_results(client, user_input, parsed, results)
        evaluation["flags"] = evaluation.get("flags", []) + ["Preferences broadened — no strong genre match found in catalog."]

    explanations = generate_explanations(client, user_input, parsed, results)

    base = taste_profile if taste_profile else {"genres": [], "moods": [], "energies": [], "request_count": 0}
    updated_profile = update_taste_profile(dict(base), parsed)

    return {
        "type": "results",
        "parsed": parsed,
        "results": results,
        "pool": pool,
        "evaluation": evaluation,
        "explanations": explanations,
        "updated_profile": updated_profile,
    }


# ── UI Components ─────────────────────────────────────────────────────────────

def render_evaluation_badge(evaluation: dict):
    confidence = evaluation.get("confidence", "medium")
    verdict = evaluation.get("verdict", "")
    contradiction = evaluation.get("contradiction_detected", False)
    contradiction_note = evaluation.get("contradiction_note", "")
    flags = evaluation.get("flags", [])

    if confidence == "high":
        st.success(f"Strong match — {verdict}")
    elif confidence == "medium":
        st.info(f"Moderate match — {verdict}")
    else:
        st.warning(f"Weak match — {verdict}")

    if contradiction and contradiction_note:
        st.warning(f"Contradiction detected: {contradiction_note}")

    for flag in flags:
        st.caption(f"Note: {flag}")


def render_song_card(song: dict, score: float, explanation: str, rank: int):
    song_id = song["id"]
    feedback = st.session_state.song_feedback.get(song_id)
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**#{rank} {song['title']}** — {song['artist']}")
            st.caption(f"{song['genre']} · {song['mood']} · Energy {song['energy']} · Score {score:.2f}")
            st.write(explanation)
            fb1, fb2, _ = st.columns([1, 1, 6])
            with fb1:
                liked = feedback == "liked"
                if st.button("Liked" if liked else "Like", key=f"like_{song_id}_{rank}", type="primary" if liked else "secondary"):
                    st.session_state.song_feedback[song_id] = None if liked else "liked"
                    st.rerun()
            with fb2:
                skipped = feedback == "skipped"
                if skipped:
                    st.button("Skipped", key=f"skip_{song_id}_{rank}", disabled=True)
                else:
                    if st.button("Skip", key=f"skip_{song_id}_{rank}", type="secondary"):
                        st.session_state.song_feedback[song_id] = "skipped"
                        pool = st.session_state.get("recommendation_pool", [])
                        if pool and st.session_state.last_results:
                            replacement = pool.pop(0)
                            st.session_state.recommendation_pool = pool
                            last = st.session_state.last_results
                            for j, entry in enumerate(last["results"]):
                                if entry[0]["id"] == song_id:
                                    rep_reason = replacement[2]
                                    last["results"][j] = replacement
                                    last["explanations"][j] = rep_reason or "Added based on your preferences."
                                    break
                        st.rerun()
        with col2:
            st.link_button("▶ Listen", youtube_url(song), use_container_width=True)


def render_results(data: dict):
    st.divider()
    parsed = data["parsed"]
    results = data["results"]
    evaluation = data["evaluation"]
    explanations = data["explanations"]

    interpreted = []
    if parsed.get("genre"):
        interpreted.append(f"Genre: **{parsed['genre']}**")
    if parsed.get("mood"):
        interpreted.append(f"Mood: **{parsed['mood']}**")
    if parsed.get("energy") is not None:
        interpreted.append(f"Energy: **{parsed['energy']}**")
    if parsed.get("lyrical_intensity") is not None:
        intensity = parsed["lyrical_intensity"]
        if intensity <= 0.1:
            intensity_label = "Mostly instrumental"
        elif intensity <= 0.4:
            intensity_label = "Light lyrics"
        elif intensity <= 0.7:
            intensity_label = "Moderate lyrics"
        else:
            intensity_label = "Heavy lyrics"
        interpreted.append(f"Lyrics: **{intensity_label}**")
    if parsed.get("lyrical_theme"):
        interpreted.append(f"Lyrical theme: **{parsed['lyrical_theme']}**")

    if interpreted:
        st.caption("Interpreted as: " + " · ".join(interpreted))

    render_evaluation_badge(evaluation)

    st.subheader("Your Recommendations")
    for i, (song, score, _) in enumerate(results):
        render_song_card(song, score, explanations[i], i + 1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="VibeCheck", page_icon="🎵", layout="centered")

    st.title("🎵 VibeCheck")
    st.caption("VibeCheck is a music recommender. Just tell us how you're feeling and we'll find the right songs for you.")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY not found. Create a .env file with your key and restart the app.")
        st.stop()

    client = genai.Client(api_key=api_key)
    catalog = load_catalog()

    if not catalog:
        st.error("Could not load the song catalog. Check that data/songs.csv exists.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_results" not in st.session_state:
        st.session_state.last_results = None
    if "taste_profile" not in st.session_state:
        st.session_state.taste_profile = {"genres": [], "moods": [], "energies": [], "request_count": 0}
    if "song_feedback" not in st.session_state:
        st.session_state.song_feedback = {}
    if "recommendation_pool" not in st.session_state:
        st.session_state.recommendation_pool = []

    if not st.session_state.messages:
        st.info(
            "**How it works:** Type how you're feeling and VibeCheck will recommend songs that match.\n\n"
            "**Try saying:**\n"
            "- *I'm tired and need something relaxing*\n"
            "- *I'm happy and want something fun to listen to*\n"
            "- *I need to focus while I study*\n"
            "- *I'm in my feelings and need music that gets it*"
        )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if st.session_state.last_results:
        render_results(st.session_state.last_results)

    if prompt := st.chat_input("e.g. I'm tired and need to relax..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ][-4:]

        with st.chat_message("assistant"):
            with st.spinner("Finding your music..."):
                try:
                    output = run_pipeline(client, catalog, prompt, history,
                                         taste_profile=st.session_state.taste_profile,
                                         song_feedback=st.session_state.song_feedback)
                except Exception as e:
                    logger.error(f"Pipeline failed: {e}")
                    st.error("Something went wrong. Please try again.")
                    st.stop()

            if output["type"] == "clarification":
                question = output["question"]
                st.write(question)
                st.session_state.messages.append({"role": "assistant", "content": question})
                st.session_state.last_results = None

            else:
                reply = f"Here are your top picks based on what you described."
                if output["evaluation"].get("contradiction_detected"):
                    reply = "I noticed your preferences have a tension — here is the best I could find."
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.last_results = output
                if "updated_profile" in output:
                    st.session_state.taste_profile = output["updated_profile"]
                if "pool" in output:
                    st.session_state.recommendation_pool = output["pool"]
                st.rerun()


if __name__ == "__main__":
    main()
