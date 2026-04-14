"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = [
        # Standard profiles
        ("High-Energy Pop",        {"genre": "pop",      "mood": "happy",   "energy": 0.92}),
        ("Chill Lofi",             {"genre": "lofi",     "mood": "chill",   "energy": 0.40}),
        ("Deep Intense Rock",      {"genre": "rock",     "mood": "intense", "energy": 0.90}),
        # Adversarial / edge case profiles
        ("Conflict: calm mood + high energy", {"genre": "lofi",      "mood": "chill",   "energy": 0.90}),
        ("Rare genre (jazz)",                 {"genre": "jazz",      "mood": "relaxed", "energy": 0.37}),
        ("No-mans-land energy",               {"genre": "pop",       "mood": "happy",   "energy": 0.50}),
        ("Genre not in catalog",              {"genre": "classical", "mood": "calm",    "energy": 0.40}),
    ]

    for label, user_prefs in profiles:
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\n" + "=" * 60)
        print(f"  Profile: {label}")
        print(f"  Genre: {user_prefs['genre']} | Mood: {user_prefs['mood']} | Energy: {user_prefs['energy']}")
        print("=" * 60)

        for rank, rec in enumerate(recommendations, start=1):
            song, score, explanation = rec
            print(f"\n#{rank}  {song['title']} -- {song['artist']}")
            print(f"    Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
            print(f"    Score: {score:.2f}")
            print(f"    Why:   {explanation}")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
