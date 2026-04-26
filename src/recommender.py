from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# Genres grouped into families for partial matching
GENRE_FAMILIES = {
    # chill
    "lofi":                    "chill",
    "ambient":                 "chill",
    "dream pop":               "chill",
    "indie folk":              "chill",
    "classical":               "chill",
    "trip-hop":                "chill",
    "chillwave":               "chill",
    "vaporwave":               "chill",
    "minimalism":              "chill",
    "contemporary classical":  "chill",
    # upbeat
    "pop":                     "upbeat",
    "indie pop":               "upbeat",
    "synthwave":               "upbeat",
    "k-pop":                   "upbeat",
    "afrobeats":               "upbeat",
    "city pop":                "upbeat",
    "art pop":                 "upbeat",
    "alternative pop":         "upbeat",
    "hyperpop":                "upbeat",
    "electropop":              "upbeat",
    "synth-pop":               "upbeat",
    "ska":                     "upbeat",
    # rock
    "rock":                    "rock",
    "indie rock":              "rock",
    "alternative":             "rock",
    "soft rock":               "rock",
    "metalcore":               "rock",
    "progressive metal":       "rock",
    "post-metal":              "rock",
    "blackgaze":               "rock",
    "shoegaze":                "rock",
    "new wave":                "rock",
    "math rock":               "rock",
    "midwest emo":             "rock",
    "emo":                     "rock",
    "pop punk":                "rock",
    "grunge":                  "rock",
    "progressive rock":        "rock",
    "psychedelic rock":        "rock",
    "post-punk":               "rock",
    "krautrock":               "rock",
    "ska punk":                "rock",
    # urban
    "hip-hop":                 "urban",
    "r&b":                     "urban",
    "reggaeton":               "urban",
    "neo-soul":                "urban",
    "funk":                    "urban",
    "motown":                  "urban",
    "gospel":                  "urban",
    "soul":                    "urban",
    # acoustic
    "flamenco":                "acoustic",
    "bossa nova":              "acoustic",
    "americana":               "acoustic",
    "country":                 "acoustic",
    "bluegrass":               "acoustic",
    "folk revival":            "acoustic",
    "reggae":                  "acoustic",
    "sea shanty":              "acoustic",
    "celtic":                  "acoustic",
    "fado":                    "acoustic",
    "tango":                   "acoustic",
    "tango nuevo":             "acoustic",
    # electronic
    "idm":                     "electronic",
    "house":                   "electronic",
    "progressive house":       "electronic",
    "trance":                  "electronic",
    "dubstep":                 "electronic",
    "drum and bass":           "electronic",
    "big beat":                "electronic",
    # jazz
    "jazz":                    "jazz",
    "big band":                "jazz",
    "bebop":                   "jazz",
    "fusion jazz":             "jazz",
    "nu jazz":                 "jazz",
    # chill (classical)
    "baroque":                 "chill",
    # cinematic
    "soundtrack":              "cinematic",
    "anime ost":               "cinematic",
    "video game ost":          "cinematic",
}

# Moods grouped into families for partial matching
MOOD_FAMILIES = {
    "happy":      "positive",
    "fun":        "positive",
    "nostalgic":  "positive",
    "hopeful":    "positive",
    "romantic":   "positive",
    "chill":      "calm",
    "relaxed":    "calm",
    "focused":    "calm",
    "peaceful":   "calm",
    "moody":      "dark",
    "dark":       "dark",
    "emotional":  "dark",
    "reflective": "dark",
    "sad":        "dark",
    "melancholic":"dark",
    "intense":    "intense",
    "aggressive": "intense",
    "angry":      "intense",
    "epic":       "intense",
}

@dataclass
class Song:
    """A single song and its audio attributes."""
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
    instrumentalness: float = 0.0
    lyrical_intensity: float = 0.0
    lyrical_theme: str = "none"
    youtube_id: str = ""

@dataclass
class UserProfile:
    """A user's taste preferences used to score and rank songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "lyrical_intensity": song.lyrical_intensity,
                "lyrical_theme": song.lyrical_theme,
            }
            score, _ = score_song(user_prefs, song_dict)
            if user.likes_acoustic and song.acousticness >= 0.70:
                score += 0.5
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "lyrical_intensity": song.lyrical_intensity,
            "lyrical_theme": song.lyrical_theme,
        }
        _, reasons = score_song(user_prefs, song_dict)
        return "; ".join(reasons) if reasons else "No strong match found"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields converted to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":                int(row["id"]),
                "title":             row["title"],
                "artist":            row["artist"],
                "genre":             row["genre"].strip().lower(),
                "mood":              row["mood"].strip().lower(),
                "energy":            float(row["energy"]),
                "tempo_bpm":         float(row["tempo_bpm"]),
                "valence":           float(row["valence"]),
                "danceability":      float(row["danceability"]),
                "acousticness":      float(row["acousticness"]),
                "instrumentalness":  float(row["instrumentalness"]),
                "lyrical_intensity": float(row["lyrical_intensity"]),
                "lyrical_theme":     row["lyrical_theme"],
                "youtube_id":        row.get("youtube_id", ""),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences. Returns (score, reasons).
    Genre: +2.0 exact / +1.0 family. Mood: +1.5 exact / +0.75 family.
    Energy: +1.0 within 0.10 / +0.5 within 0.25. Lyrical intensity: +0.75/+0.35. Theme: +0.50."""
    score = 0.0
    reasons = []

    user_genre = user_prefs.get("genre", "")
    song_genre = song.get("genre", "")
    if song_genre == user_genre:
        score += 2.0
        reasons.append(f"genre match (+2.0)")
    elif GENRE_FAMILIES.get(song_genre) == GENRE_FAMILIES.get(user_genre) and user_genre:
        score += 1.0
        reasons.append(f"similar genre: {song_genre} is in the same family as {user_genre} (+1.0)")

    user_mood = user_prefs.get("mood", "")
    song_mood = song.get("mood", "")
    if song_mood == user_mood:
        score += 1.5
        reasons.append(f"mood match (+1.5)")
    elif MOOD_FAMILIES.get(song_mood) == MOOD_FAMILIES.get(user_mood) and user_mood:
        score += 0.75
        reasons.append(f"similar mood: {song_mood} is in the same family as {user_mood} (+0.75)")

    user_energy = user_prefs.get("energy")
    if user_energy is not None:
        diff = abs(song["energy"] - user_energy)
        if diff <= 0.10:
            score += 1.0
            reasons.append(f"energy close match: {song['energy']} ~= {user_energy} (+1.0)")
        elif diff <= 0.25:
            score += 0.5
            reasons.append(f"energy partial match: {song['energy']} near {user_energy} (+0.5)")

    user_lyrical = user_prefs.get("lyrical_intensity")
    if user_lyrical is not None:
        diff = abs(song.get("lyrical_intensity", 0.0) - user_lyrical)
        if diff <= 0.15:
            score += 0.75
            reasons.append(f"lyrical intensity match (+0.75)")
        elif diff <= 0.30:
            score += 0.35
            reasons.append(f"lyrical intensity partial match (+0.35)")

    user_theme = user_prefs.get("lyrical_theme")
    if user_theme and user_theme != "none":
        if song.get("lyrical_theme") == user_theme:
            score += 0.50
            reasons.append(f"lyrical theme match: {user_theme} (+0.50)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort highest to lowest, return top k.
    The requested genre is uncapped; all other genres are capped at 2 for diversity."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "No strong match found"
        scored.append((song, score, explanation))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    preferred_genre = user_prefs.get("genre", "")
    results: List[Tuple[Dict, float, str]] = []
    genre_counts: Dict[str, int] = {}
    overflow: List[Tuple[Dict, float, str]] = []
    for item in ranked:
        genre = item[0]["genre"]
        cap = float("inf") if genre == preferred_genre else 2
        count = genre_counts.get(genre, 0)
        if count < cap:
            results.append(item)
            genre_counts[genre] = count + 1
        else:
            overflow.append(item)
        if len(results) == k:
            break

    for item in overflow:
        if len(results) >= k:
            break
        results.append(item)

    return results[:k]
