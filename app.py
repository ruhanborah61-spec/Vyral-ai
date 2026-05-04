import streamlit as st
import requests
import re

# ---------------- API ----------------
API_KEY = st.secrets["GROQ_API_KEY"]

if not API_KEY:
    st.error("Missing API Key")
    st.stop()

# ---------------- GAME LAYER ----------------
GAME_LAYER = {
    "Valorant": {
        "situations": "whiffing easy shots, toxic teammate, insta-lock duelist, clutch 1v2, eco round panic",
        "mechanics": "crosshair placement, spray control, peeking, utility misuse",
        "visuals": "buy phase, spike plant, scoreboard, kill feed, 1v1 clutch"
    },

    "CS2": {
        "situations": "rush B fail, eco round win, smoke miss, A site retake chaos",
        "mechanics": "recoil spray, crosshair placement, peek timing, grenade usage",
        "visuals": "bomb plant, smoke walls, scoreboard, headshot kill feed"
    },

    "BGMI": {
        "situations": "hot drop death, camping enemy, last zone panic, squad wipe",
        "mechanics": "recoil control, loot rush, zone rotation, grenade spam",
        "visuals": "airdrop, zone shrink, kill feed, prone camping fights"
    },

    "Free Fire": {
        "situations": "gloo wall spam, rush fail, sniper miss, squad betrayal",
        "mechanics": "movement spam, gloo wall placement, aim drag",
        "visuals": "revive, gloo wall fights, fast kills, loot box"
    },

    "Minecraft": {
        "situations": "lava fall, creeper explosion, diamond loss, bed destroyed",
        "mechanics": "building fail, PvP knockback, mining risk",
        "visuals": "bed break, crafting table, death screen"
    },

    "Bedwars": {
        "situations": "bed destroyed instantly, final 1v1 loss, bridge fail",
        "mechanics": "bridging, rushing, TNT attack, resource camping",
        "visuals": "island fight, bed break, void fall"
    }
}

# fallback
DEFAULT_GAME = {
    "situations": "mistake, clutch fail, teammate trolling",
    "mechanics": "basic gameplay actions",
    "visuals": "gameplay clips, scoreboard, kill feed"
}

def get_game(game):
    return GAME_LAYER.get(game, DEFAULT_GAME)

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
        "temperature": 0.95
    }

    res = requests.post(url, json=data, headers=headers)

    if res.status_code != 200:
        return "API ERROR"

    return res.json()["choices"][0]["message"]["content"]

def clean(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# ---------------- PROMPT ENGINE ----------------
def generate_meme(game, idea):

    g = get_game(game)

    prompt = f"""
You are a FRAME-BY-FRAME GAMEPLAY CAPTION SYSTEM.

You are NOT allowed to connect events logically.

You ONLY describe what happens in each frame independently.

----------------------

GAME: {game}
IDEA: {idea}

----------------------

CRITICAL RULE:

Each time segment MUST be independent.
NO cause-effect storytelling.

Example of WRONG:
"enemy destroys bridge so player falls"

Example of CORRECT:
"bridge missing block"
"player in void falling"

----------------------

ONLY ALLOWED OUTPUT STYLE:

- visible actions
- visible game objects
- visible results on screen

NO:
- explanation
- reasoning
- story flow
- "because"
- "so"
- "therefore"

----------------------

OUTPUT FORMAT:

🚀 TITLE:
max 4 words, meme tone

🔥 HOOK:
VISUAL: single frame only
TEXT: 2–4 words max

📋 EXECUTION:

0–3 sec:
frame action ONLY

3–7 sec:
new frame action ONLY (no connection to previous line)

7–12 sec:
new frame action ONLY

12–18 sec:
final screen state ONLY

💥 FINAL PAYOFF:
short meme text (no explanation)

💡 WHY IT WORKS:
ONLY:
“fast cuts + visible mistakes + payoff”

----------------------

❌ FORBIDDEN:
- cause-effect logic
- storytelling
- narration
- cinematic phrasing
- fake game mechanics
"""
    return call_groq(prompt)

# ---------------- UI ----------------
st.set_page_config(page_title="Vyral Meme Engine", page_icon="🎮")

st.title("🎮 Vyral Meme Engine")
st.write("Gaming meme script generator (Shorts-ready)")

game = st.selectbox("Game", list(GAME_LAYER.keys()))
idea = st.text_input("Enter idea (e.g. whiff, clutch fail, toxic teammate)")

btn = st.button("Generate Meme Script")

if btn:
    if not idea:
        st.error("Enter idea")
    else:
        with st.spinner("Generating viral meme..."):
            result = generate_meme(game, idea)

        st.markdown("## 🚀 OUTPUT")
        st.write(clean(result))