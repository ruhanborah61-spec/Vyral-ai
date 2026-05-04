import streamlit as st
import requests
import re
import random

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ Missing GROQ_API_KEY in Streamlit secrets")
    st.stop()

# ---------------- GAME KNOWLEDGE (MULTI-GAME) ----------------
GAME_KNOWLEDGE = {
    "Valorant": {
        "mechanics": "crosshair placement, whiffing, spray control, peeking, clutching",
        "visuals": "buy phase, scoreboard, kill feed, minimap, site entry, defuse",
        "situations": "1v1 clutch, toxic teammate, insta-lock duelist, eco round, whiff moments"
    },
    "BGMI": {
        "mechanics": "recoil control, drop timing, zone rotation, grenade usage, close combat",
        "visuals": "loot phase, red zone, zone shrink, squad push, death screen",
        "situations": "hot drop, third party fight, last zone 1v2, prone campers"
    },
    "CS2": {
        "mechanics": "aim pre-fire, spray control, counter-strafe, site hold, flash timing",
        "visuals": "bomb plant, defuse, scoreboard, smoke wall, entry frag",
        "situations": "eco round upset, clutch defuse, rush B fail, A site hold"
    }
}

def get_game_info(game):
    return GAME_KNOWLEDGE.get(game, GAME_KNOWLEDGE["Valorant"])

# ---------------- VIRAL PATTERNS ----------------
VIRAL_PATTERNS = {
    "Meme & Comedy": "failure → chaos → blame → funny payoff",
    "Teaching (tips & tricks)": "mistake → fix → instant improvement",
    "Clutch moments & highlights": "pressure → survival → win moment",
    "Rank up journey": "bad play → realization → improvement clip"
}

HOOK_BANK = [
    "Why you losing fights",
    "This is a free kill",
    "Stop doing this",
    "He missed everything",
    "Watch this mistake"
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
        "temperature": 0.9
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code != 200:
        return f"API Error: {r.text}"

    return r.json()["choices"][0]["message"]["content"]

def clean(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

# ---------------- PROMPT ENGINE (CORE FIX) ----------------
def generate_idea(name, followers, engagement, game, style):
    g = get_game_info(game)

    pattern = VIRAL_PATTERNS.get(style, "gameplay mistake → reaction → result")
    hook = random.choice(HOOK_BANK)

    prompt = f"""
You are NOT a storyteller.

You are a PROFESSIONAL SHORTS GAMEPLAY EDITOR.

You only describe RAW gameplay clips that can be recorded.

NO emotions. NO narration. NO cinematic writing.

CREATOR:
{name}
Followers: {followers}
Game: {game}
Style: {style}
Engagement: {engagement}%

EDIT STYLE:
{pattern}

GAME DATA:
Mechanics: {g['mechanics']}
Visuals: {g['visuals']}
Situations: {g['situations']}

RULES:
- Only real gameplay actions
- No imagination
- No dialogue
- No storytelling
- Every line must be filmable

OUTPUT FORMAT:

🚀 BEST VIDEO IDEA

🎬 TITLE:
[short gameplay title]

🔥 HOOK (0–2 sec)
VISUAL:
[exact in-game frame]
TEXT:
[3–5 word hook]

📋 EXECUTION

0–5 SEC:
[raw gameplay action]

TEXT:
[short text]

5–12 SEC:
[next gameplay action]

TEXT:
[short text]

12–18 SEC:
[final gameplay action]

FINAL 2 SEC:
[result screen]

TEXT:
[punchline]

💡 WHY IT WORKS:
[one line: mistake → fix → payoff]

"""

    return clean(call_groq(prompt))

# ---------------- UI ----------------
st.set_page_config(page_title="Vyral", page_icon="🎮")

st.title("Vyral 🎮")
st.write("Real gameplay viral idea generator")

st.sidebar.header("Profile")

name = st.sidebar.text_input("Name")
followers = st.sidebar.number_input("Followers", min_value=0)
likes = st.sidebar.number_input("Avg likes", min_value=0)

game = st.sidebar.selectbox("Game", list(GAME_KNOWLEDGE.keys()))
style = st.sidebar.selectbox("Style", [
    "Meme & Comedy",
    "Teaching (tips & tricks)",
    "Clutch moments & highlights",
    "Rank up journey"
])

analyze = st.sidebar.button("Generate")

# ---------------- MAIN ----------------
if analyze:
    if followers == 0:
        st.error("Add followers")
    elif not name:
        st.error("Add name")
    else:
        engagement = round((likes / followers) * 100, 2) if followers else 0

        with st.spinner("Generating REAL viral idea..."):
            idea = generate_idea(name, followers, engagement, game, style)

        st.write(idea)