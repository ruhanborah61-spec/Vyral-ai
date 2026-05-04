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
You are a VIRAL SHORT-FORM RETENTION ENGINE.

You do NOT write stories.
You do NOT explain.
You do NOT analyze.

You ONLY generate FAST CUT MEME GAMEPLAY SCRIPTS.

----------------------

⚠️ CORE RULE:
Everything must feel like a 7–18 second edited clip with rapid cuts.

No filler. No explanation. No storytelling.

----------------------

GAME: {game}
IDEA: {idea}

GAME LIMITS (STRICT):
Use ONLY these actions:

- VISUALS: {g['visuals']}
- SITUATIONS: {g['situations']}
- MECHANICS: {g['mechanics']}

DO NOT invent anything outside this.

----------------------

🔥 RETENTION ENGINE RULES:

- First 1 second MUST create confusion or embarrassment
- Every 3–5 seconds MUST escalate tension
- No calm moments allowed
- No explanation sentences
- Every line = visible gameplay action only

----------------------

MEME FLOW (MANDATORY):

HOOK → MISTAKE → ESCALATION → CHAOS → EMBARRASSMENT PAYOFF

----------------------

OUTPUT FORMAT:

🚀 TITLE:
max 4–5 words, ironic or funny

🔥 HOOK (0–2 sec):
VISUAL: single frozen frame action
TEXT: 2–4 words ONLY (shock or confusion)

📋 EXECUTION (FAST CUT STYLE):

0–3 sec:
single gameplay action (mistake begins)

3–7 sec:
mistake becomes obvious or worse

7–12 sec:
chaos escalation (enemy/team reacts ONLY if visible in game)

12–18 sec:
final fail or loss moment

💥 FINAL PAYOFF:
1 short meme line (failure punchline only)

💡 WHY IT WORKS:
ONLY ONE LINE:
“fast escalation + relatable mistake + instant payoff”

----------------------

❌ HARD FORBIDDEN:
- storytelling ("he tried", "he realized")
- emotions ("panic", "sad", "frustrated")
- cinematic language
- explanations
- analysis
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