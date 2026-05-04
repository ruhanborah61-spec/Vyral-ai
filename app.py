import streamlit as st
import requests
import re
import random

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ Missing GROQ_API_KEY in Streamlit secrets")
    st.stop()

# ---------------- GAME KNOWLEDGE ----------------
GAME_KNOWLEDGE = {
    "Valorant": {
        "mechanics": "crosshair placement, whiffing, spray control, peeking, clutching",
        "visuals": "buy phase, scoreboard, kill feed, minimap, clutch moments",
        "situations": "toxic teammate, insta-lock duelist, throw rounds, team arguing, clutch pressure",
        "meme_lines": "trust me bro, team diff, uninstall, nice try, lag, noob team"
    }
}

def get_game_info(game):
    return GAME_KNOWLEDGE.get(game, GAME_KNOWLEDGE["Valorant"])

# ---------------- VIRAL MEMORY ----------------
VIRAL_PATTERNS = {
    "Meme & Comedy": [
        "teammate ego collapse",
        "relatable rage moment",
        "fake carry exposed",
        "team chaos",
    ],
    "Teaching (tips & tricks)": [
        "mistake → fix → result",
        "before vs after improvement",
    ],
    "Clutch moments & highlights": [
        "1vX clutch",
        "impossible survival",
    ],
    "Rank up journey": [
        "rank struggle → improvement",
        "before vs after stats"
    ]
}

HOOKS = [
    "He said he will carry 💀",
    "This is why you lose",
    "Stop doing this now",
    "You're throwing games",
    "Most players miss this",
]

# ---------------- API CALL ----------------
def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen/qwen3-32b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return f"API Error: {response.text}"

    return response.json()["choices"][0]["message"]["content"]

def clean_response(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

# ---------------- PROMPT ENGINE ----------------
def get_ai_suggestions(name, followers, engagement, game, platform, style, about, feedback=""):
    game_info = get_game_info(game)

    pattern = random.choice(VIRAL_PATTERNS.get(style, ["relatable gameplay moment"]))
    hook = random.choice(HOOKS)

    feedback_text = f"\nFix this: {feedback}" if feedback else ""

    prompt = f"""
You are a RAW GAMING CLIP EDITOR for viral Shorts.

You DO NOT tell stories.
You ONLY describe real gameplay edits.

CREATOR:
{name}
Followers: {followers}
Engagement: {engagement}%
Game: {game}
Style: {style}

CONTENT MODE:
{pattern}

GAME DATA:
Mechanics: {game_info['mechanics']}
Situations: {game_info['situations']}
Visuals: {game_info['visuals']}

⚔️ EXECUTION RULES (VERY IMPORTANT):
- No storytelling
- No emotions
- No cinematic narration
- No "enemy confused", "player feels", "clutch moment"
- ONLY describe screen actions
- Every line must be filmable gameplay
- Keep it messy, real, raw (like actual clips)

🔥 HOOK RULES:
- Max 5 words
- Must sound like real player reaction
- No formatting like [PAUSE], no caps spam

OUTPUT FORMAT (STRICT):

🚀 BEST VIDEO IDEA FOR YOU (HIGH VIRAL POTENTIAL)

🎬 Title:
[short punchy gaming title]

🔥 Hook (0–2 sec)
Visual:
[exact gameplay frame — raw]

Text:
[short hook line]

📋 Execution

0–5 sec:
[exact gameplay action only]

Text:
[simple on-screen text]

5–12 sec:
[next gameplay action only]

Text:
[simple reaction text]

12–18 sec:
[last gameplay action]

Final 2 sec (PAYOFF):
[result clip only]

Text:
[final punchline]

💡 Why this works:
[ONE simple reason: pain / relatable / improvement / chaos]

❌ Avoid:
- cinematic edits
- fake emotions
- over explanation

{feedback_text}
"""
    return call_groq(prompt)
# ---------------- SCORING ----------------
def score_post(name, post_idea, followers):
    prompt = f"""
Analyze this gaming video idea.

Creator: {name}
Followers: {followers}

Idea:
{post_idea}

Return:

HOOK SCORE: X/100
SHAREABILITY: X/100
TREND MATCH: X/100
AUDIENCE FIT: X/100

WEAKNESS: one line
FIX: one action
VERDICT: POST IT or FIX FIRST
"""
    return call_groq(prompt)

# ---------------- UI ----------------
st.set_page_config(page_title="Vyral", page_icon="🎮")

st.title("Vyral 🎮")
st.write("AI content coach for gaming creators")

st.sidebar.header("Your Profile")

name = st.sidebar.text_input("Your name")
followers = st.sidebar.number_input("Followers", min_value=0)
likes = st.sidebar.number_input("Avg likes per post", min_value=0)

game = st.sidebar.selectbox("Your game", ["Valorant"])

platform = st.sidebar.selectbox("Where do you post?", [
    "YouTube Shorts", "Instagram Reels", "TikTok"
])

style = st.sidebar.selectbox("Your content style", [
    "Teaching (tips & tricks)",
    "Meme & Comedy",
    "Clutch moments & highlights",
    "Rank up journey"
])

about = st.sidebar.text_area("About you")

analyze = st.sidebar.button("⚡ Analyze")

# ---------------- MAIN LOGIC ----------------
if analyze:
    if followers == 0:
        st.error("Enter followers")
    elif not name:
        st.error("Enter name")
    else:
        engagement = round((likes / followers) * 100, 2) if followers else 0

        with st.spinner("Generating viral idea..."):
            result = get_ai_suggestions(
                name, followers, engagement,
                game, platform, style, about
            )

        st.write(clean_response(result))

# ---------------- SCORING ----------------
st.sidebar.divider()
st.sidebar.subheader("🎯 Score idea")

post_idea = st.sidebar.text_area("Describe idea")
score_btn = st.sidebar.button("Score")

if score_btn and post_idea:
    with st.spinner("Scoring..."):
        score = score_post(name, post_idea, followers)
    st.write(clean_response(score))