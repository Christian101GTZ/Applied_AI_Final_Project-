# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeCheck 2.0**

---

## 2. Intended Use

VibeCheck is designed to suggest songs that match how a user wants to feel. You describe what you want in plain English — "something dark and cinematic" or "chill lofi for studying" — and a Gemini-powered agent translates that into structured preferences, scores a catalog of 300 songs, evaluates the results, and explains each recommendation in natural language.

**Not intended for:** replacing real music apps, large-scale production, or making decisions for actual listeners without human review.

---

## 3. How the Model Works

The system scores every song in the catalog against what the user asked for. It checks three things:

- **Genre** -- does the song match the user's genre? An exact match earns 2 points. A song from a related genre (like indie pop when you asked for pop) earns 1 point.
- **Mood** -- does the song match the user's mood? An exact match earns 1.5 points. A similar mood (like fun when you asked for happy) earns 0.75 points.
- **Energy** -- how close is the song's energy to what the user wants? Very close earns 1 point. Somewhat close earns 0.5 points. Too far off earns nothing.

Every song gets a total score. The system sorts all songs from highest to lowest and returns the top 5. The "Why" line in the output explains exactly which points each song earned.

---

## 4. Data

The catalog contains 300 songs stored in `data/songs.csv`. Each song has 14 attributes. Here is what every attribute means and how it is measured:

---

### Song Identity Fields

| Attribute | Type | What it means |
|---|---|---|
| `id` | Integer | Unique number identifying each song |
| `title` | Text | The name of the song |
| `artist` | Text | The performer or band |
| `genre` | Text | The musical style (see genre list below) |
| `mood` | Text | The emotional feeling the song creates (see mood list below) |
| `youtube_id` | Text | The YouTube video ID used to build a direct listen link |

---

### Audio Feature Fields

These attributes describe how a song sounds. They are modeled after the audio analysis features used by streaming platforms like Spotify.

| Attribute | Scale | What 0.0 means | What 1.0 means | Example |
|---|---|---|---|---|
| `energy` | 0.0 – 1.0 | Very quiet, slow, calm | Very loud, fast, intense | *Gymnopedie No.1* = 0.12 vs *Gym Hero* = 0.93 |
| `tempo_bpm` | 40 – 200+ | Very slow, ballad pace | Very fast, punk or metal pace | *Time* = 52 bpm vs *Blinding Lights* = 171 bpm |
| `valence` | 0.0 – 1.0 | Dark, sad, tense sound | Bright, happy, uplifting sound | *Moonlight Sonata* = 0.22 vs *Sunrise City* = 0.84 |
| `danceability` | 0.0 – 1.0 | Hard to dance to, irregular rhythm | Made for dancing, strong steady beat | *Time* = 0.20 vs *Despacito* = 0.86 |
| `acousticness` | 0.0 – 1.0 | Fully electronic, synthesized sound | Fully acoustic, natural instruments only | *Turbo Killer* = 0.03 vs *Clair de Lune* = 0.98 |
| `instrumentalness` | 0.0 – 1.0 | Song has vocals throughout | Song is fully instrumental, no singing | *Blinding Lights* = 0.05 vs *Time* = 0.98 |

---

### Lyrical Fields

These attributes describe what the lyrics do, not how the music sounds. A song can be acoustically soft but lyrically intense. For example *Holocene* by Bon Iver sounds calm but carries heavy lyrical weight. This separation is what allows the system to handle requests like "something relaxing but with intense lyrics."

| Attribute | Scale | What it measures |
|---|---|---|
| `lyrical_intensity` | 0.0 – 1.0 | How emotionally heavy or dense the lyrics are. 0.0 means no lyrics at all. 1.0 means extremely raw, intense, or emotionally heavy lyrics. |
| `lyrical_theme` | Text label | The subject matter of the lyrics. Values: `none` (instrumental), `love`, `loss`, `struggle`, `motivation`, `reflection`, `nostalgia`, `darkness`, `celebration`, `abstract` |

---

### Genres in the Catalog

#### Chill

| Genre | Family | Sound description |
|---|---|---|
| lofi | chill | Low-fidelity beats, background-friendly |
| ambient | chill | Texture-based, no strong melody or beat |
| dream pop | chill | Hazy, atmospheric, soft vocals |
| indie folk | chill | Acoustic storytelling, intimate feel |
| classical | chill | Orchestral or solo instrument, no vocals |
| trip-hop | chill | Slow beats, cinematic atmosphere, melancholic |
| chillwave | chill | Soft, washed-out synths, mellow and hazy |
| vaporwave | chill | Nostalgic 80s aesthetics, slowed and pitched audio |
| minimalism | chill | Sparse, repetitive structures, meditative texture |
| contemporary classical | chill | Modern composed instrumental, concert hall or ambient |

#### Upbeat

| Genre | Family | Sound description |
|---|---|---|
| pop | upbeat | Mainstream, polished, hook-driven |
| indie pop | upbeat | Lighter alternative pop, less produced |
| synthwave | upbeat | 80s-inspired electronic, neon atmosphere |
| k-pop | upbeat | Polished Korean pop, high-energy choreography |
| afrobeats | upbeat | West African rhythms blended with pop and dancehall |
| city pop | upbeat | 80s Japanese urban pop, smooth and nostalgic |
| art pop | upbeat | Experimental pop with strong artistic vision |
| alternative pop | upbeat | Pop with alternative edge, less mainstream polish |
| hyperpop | upbeat | Maximalist, hyper-compressed, internet-era pop |
| electropop | upbeat | Electronic-driven pop, danceable and synth-forward |
| synth-pop | upbeat | 80s keyboard-driven pop with electronic texture |
| ska | upbeat | Upstroke guitar rhythms, brass section, Caribbean roots |

#### Rock

| Genre | Family | Sound description |
|---|---|---|
| rock | rock | Guitar-driven, broad range of intensity |
| indie rock | rock | Guitar-driven alternative, indie sensibility |
| alternative | rock | Broad guitar rock outside mainstream pop |
| soft rock | rock | Melodic, mellow guitar rock |
| metalcore | rock | Heavy guitars, screamed vocals, breakdowns |
| progressive metal | rock | Complex structures, shifting time signatures |
| post-metal | rock | Slow, atmospheric heaviness |
| blackgaze | rock | Black metal blended with shoegaze texture |
| shoegaze | rock | Dense wall of guitar sound, dreamy and distorted |
| new wave | rock | 80s post-punk energy, synth-driven |
| math rock | rock | Complex rhythms, mostly instrumental, technical |
| midwest emo | rock | Confessional lyrics, quiet-loud dynamics |
| emo | rock | Raw emotional lyrics, loud-quiet-loud dynamics |
| pop punk | rock | Catchy melodies fused with punk energy |
| grunge | rock | Distorted guitars, apathetic tone, Seattle sound |
| progressive rock | rock | Extended structures, concept albums, instrumental complexity |
| psychedelic rock | rock | Mind-altering sound design, experimental arrangements |
| post-punk | rock | Cold, angular guitar lines, minimal and urgent |
| krautrock | rock | German experimental rock, motorik beat, hypnotic |
| ska punk | rock | Ska rhythm meets punk aggression |

#### Urban

| Genre | Family | Sound description |
|---|---|---|
| hip-hop | urban | Rap-driven, rhythm-focused, beat-heavy |
| r&b | urban | Soulful vocals, smooth grooves |
| reggaeton | urban | Latin urban beat, heavy bass, danceable |
| neo-soul | urban | Organic soul with modern R&B influence |
| funk | urban | Groove-heavy, danceable, bass-driven |
| motown | urban | Classic soul-pop from Detroit, tight arrangements |
| gospel | urban | Spiritual themes, call-and-response, vocal power |
| soul | urban | Heartfelt vocals, R&B roots, emotional depth |

#### Acoustic

| Genre | Family | Sound description |
|---|---|---|
| flamenco | acoustic | Spanish guitar, passionate, rhythmically complex |
| bossa nova | acoustic | Brazilian jazz fusion, gentle and intimate |
| americana | acoustic | Roots music blending country, folk, and blues |
| country | acoustic | Storytelling, twang guitar, Southern American roots |
| bluegrass | acoustic | Fast picking, banjo and fiddle, Appalachian tradition |
| folk revival | acoustic | 1960s-inspired folk, acoustic storytelling |
| reggae | acoustic | Offbeat rhythm guitar, Jamaican roots, social themes |
| sea shanty | acoustic | Maritime work songs, communal call-and-response |
| celtic | acoustic | Irish and Scottish folk traditions, fiddle and pipes |
| fado | acoustic | Portuguese melancholy, mournful vocals, minor keys |
| tango | acoustic | Argentine dance music, sharp rhythms, passionate drama |
| tango nuevo | acoustic | Modern tango with jazz and classical influence |

#### Electronic

| Genre | Family | Sound description |
|---|---|---|
| IDM | electronic | Intelligent dance music, complex beats for listening |
| house | electronic | Chicago-born dance music, four-on-the-floor kick |
| progressive house | electronic | Long-building house tracks, gradual drops |
| trance | electronic | Repetitive melodies, high BPM, euphoric builds |
| dubstep | electronic | Heavy bass wobbles, half-time rhythms, intense drops |
| drum and bass | electronic | Fast breakbeats, heavy bass, high energy |
| big beat | electronic | Sample-heavy electronic rock, late 90s club sound |

#### Jazz

| Genre | Family | Sound description |
|---|---|---|
| jazz | jazz | Improvisation-driven, complex harmony |
| baroque | jazz | Ornate Baroque-era composition, harpsichord and counterpoint |
| big band | jazz | Large ensemble jazz, swinging brass and rhythm section |
| bebop | jazz | Fast tempos, complex chords, virtuosic improvisation |
| fusion jazz | jazz | Jazz blended with rock or funk |
| nu jazz | jazz | Modern jazz fused with electronic or hip-hop elements |

#### Cinematic

| Genre | Family | Sound description |
|---|---|---|
| soundtrack | cinematic | Written for film or TV, narrative atmosphere |
| anime ost | cinematic | Japanese animation scores, emotional and melodic |
| video game ost | cinematic | Interactive media scores, looping and adaptive |

---

### Moods in the Catalog

| Mood | Family | What it feels like |
|---|---|---|
| happy | positive | Bright, feel-good, energetic joy |
| fun | positive | Playful, carefree, light |
| nostalgic | positive | Warm memories, bittersweet brightness |
| hopeful | positive | Forward-looking, emotionally uplifting |
| romantic | positive | Tender, intimate, loving |
| chill | calm | Relaxed, low-stimulation, easy listening |
| relaxed | calm | Peaceful, unhurried, comfortable |
| focused | calm | Clear-headed, non-distracting, steady |
| peaceful | calm | Still, serene, meditative |
| sad | dark | Heavy-hearted, tearful, emotionally low |
| melancholic | dark | Quietly sorrowful, reflective sadness |
| emotional | dark | Raw feeling, vulnerability, depth |
| reflective | dark | Thoughtful, introspective, slow-moving |
| moody | dark | Unsettled, atmospheric, ambiguous |
| dark | dark | Heavy atmosphere, tension, shadow |
| intense | intense | Urgent, high-pressure, driving |
| aggressive | intense | Sharp, confrontational, hard-hitting |
| angry | intense | Raw frustration, high-energy tension |
| epic | intense | Grand, swelling, cinematic scale |

---

## 5. Strengths

- Works well when the user's taste matches what is already in the catalog. Pop, lofi, and rock users all get strong, clear top picks.
- The partial match system (genre and mood families) means the system can still find related songs even when there is no exact match.
- Every recommendation comes with a plain-language explanation of why it was chosen, which makes the system transparent and easy to understand.
- The system never crashes, even when the requested genre is not in the catalog at all.

---

## 6. Limitations and Bias

The biggest weakness is that mid-range energy users get a worse experience. The catalog has almost no songs with energy around 0.5 -- songs are either slow or fast with very little in between. So a user who wants medium energy gets no energy points at all, and their recommendations are decided only by genre and mood. High-energy and low-energy users get the full scoring system. Mid-energy users do not. That is unfair and the system does not warn the user about it.

Genre also has a lot of power. At 2 points it is the highest-weighted attribute, which means a user can get stuck in their genre even when songs from other genres would fit their mood and energy perfectly. When a user's preferences conflict -- for example, calm lofi music but high energy -- the Gemini Agent detects the contradiction at the input layer and warns the user before scoring begins. However, the scoring engine itself has no mechanism to resolve the conflict: it still returns the best available matches within the requested genre, which will not satisfy the energy preference. The warning informs the user but does not change the results.

---

## 7. Evaluation

Seven profiles were tested in total. Three were normal profiles -- High-Energy Pop, Chill Lofi, and Deep Intense Rock -- to check that the system works when the user's taste matches what is in the catalog. All three gave strong results with clear top picks, which means the basic scoring logic is working.

Four harder profiles were also tested to see where the system breaks down. One asked for calm lofi music but with high energy, which is a contradiction. One asked for jazz. One asked for energy 0.5, which is sparse in the catalog. One asked for classical.

The most surprising result was the conflict profile. The system recommended slow, quiet lofi songs to a user who asked for high energy -- because genre and mood scored more points than energy. The Gemini Agent detects this contradiction at the input layer and warns the user before scoring begins.

With the expanded 300-song catalog, the jazz and classical profiles now return genuine matches with meaningful score separation. Jazz has 9 songs spanning relaxed to epic moods. Classical has 9 songs. The catalog spans 78 genres across 8 families, so niche requests surface real matches and the family system handles requests that don't name an exact genre.

A weight shift experiment was also run where genre points were cut in half and energy points were doubled. The results got worse -- a dark synthwave song tied with a happy pop song for the same user profile, which made no sense. The original weights were restored.

---

## 8. Future Work

- **Increase coverage for sparse genres.** Several genres in the 300-song catalog have only 1–2 songs (e.g., dubstep, progressive house, ska punk, fado, bluegrass, tango). A user requesting these genres will get a correct match but almost no variety. Adding 4–6 songs per under-represented genre would give the diversity cap in `recommend_songs` room to work properly.

- **Persist the taste profile across sessions.** The session personalization system — which tracks the genres, moods, and energy levels a user has gravitated toward — currently resets every time the app restarts. Saving this profile to a file or local database would allow the system to remember returning users and make smarter recommendations from the first message of a new session.

- **Connect feedback to scoring weights.** The Like and Skip buttons currently send a summary of liked songs back to the AI as context in the prompt. This influences the natural language explanations but does not change the actual scoring weights in the recommender algorithm. A stronger implementation would adjust genre, mood, and energy weights dynamically based on what the user has explicitly liked or skipped, making the recommendations improve measurably over a session.

- **Warn the user when catalog coverage is poor.** If the user requests a genre or mood that has very few songs in the catalog, the system should say so rather than quietly returning weak results. A simple check — if the top-5 scores are all below a threshold, surface a note like "we have limited songs in this genre" — would set honest expectations.

- **Upgrade API quota.** The current deployment uses `gemini-2.5-flash` on the free tier, which allows only 20 requests per day. Since each user interaction consumes 3 API calls (intent parsing, result evaluation, and explanation generation), the system supports roughly 6 full interactions before hitting the daily limit. Adding billing would remove this constraint and allow the app to be used freely without rationing requests.

---

## 9. Personal Reflection

Building this showed me that a recommender is only as good as the data behind it. The scoring logic worked exactly as designed, but the results still felt wrong in some cases -- not because the code was broken, but because the catalog was too small or unbalanced. That was unexpected. I assumed getting the math right was the hard part, but choosing what to score and how much weight to give each thing turned out to matter just as much. It also made me think differently about apps like Spotify. When a recommendation feels off, it is probably not a bug -- it is the system making a trade-off between different signals, just like VibeCheck does.
