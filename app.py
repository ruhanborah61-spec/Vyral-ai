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
You are a STRICT VIRAL GAMEPLAY CAPTION ENGINE.

Your job is to turn an idea into a SHORT-FORM GAME MEME SCRIPT.

You do NOT tell stories.
You do NOT analyze.
You do NOT assume hidden information.
You ONLY describe what is visible on screen like a gameplay recording.

----------------------------

GAME: {game}
IDEA: {idea}

----------------------------

ABSOLUTE CORE RULES:

1. EVERY LINE MUST BE A CAMERA FRAME DESCRIPTION, NOT A GAME EVENT.
2. ONLY describe visible screen actions
3. NO storytelling (no “tries”, “plans”, “realizes”, “accidentally”)
4. NO global awareness (no “all enemies”, “entire team” unless visible)
5. NO cinematic writing
6. NO emotions or commentary
7. NO “because”, “so”, “then he realizes”.
8. Each line = one screen moment ONLY

---------------------------

FRAME RULE:

Each line must answer:
“What would a viewer see in a screen recording at this exact second?”

If it cannot be recorded → REMOVE IT.

----------------------------

VALID CONTENT ONLY:
- player movement
- shooting / hitting / missing
- building / placing / breaking (game dependent)
- UI elements (kill feed, HP, score, death screen)
- visible enemies or objects

----------------------------

MEME STRUCTURE (FAST CUT STYLE):

HOOK → ACTION → MISTAKE → ESCALATION → RESULT

Each segment MUST be visually observable.

----------------------------

OUTPUT FORMAT:

🚀 TITLE:
max 4–5 words, meme tone

🔥 HOOK (0–2 sec):
VISUAL: one screen frame only
TEXT: 2–4 words max

📋 EXECUTION:

0–3 sec:
only visible gameplay action

3–7 sec:
next visible action (no explanation, no logic)

7–12 sec:
visible escalation on screen

12–18 sec:
final visible result screen (win/loss/death)

💥 FINAL PAYOFF:
short meme line (funny fail or outcome only)

💡 WHY IT WORKS:
one line only:
“fast visible actions + escalating mistake + payoff”

----------------------------

SELF-CHECK (IMPORTANT BEFORE FINAL ANSWER):

Before responding, verify:
- Did I add anything not visible on screen? → REMOVE IT
- Did I assume hidden info? → REMOVE IT
- Did I explain instead of show? → REMOVE IT

Return ONLY cleaned output.
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