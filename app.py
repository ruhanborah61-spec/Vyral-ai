import streamlit as st
import requests
import re

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("Missing API Key")
    st.stop()

# ---------------- GAME LAYER ----------------
GAME_LAYER = {
    "Valorant": {
        "situations": "whiffing shots, eco round panic, spike plant chaos, clutch pressure",
        "mechanics": "aim, recoil, peeking, ability usage, crosshair placement",
        "visuals": "kill feed, spike, scoreboard, HUD, death screen"
    },

    "CS2": {
        "situations": "rush fail, smoke miss, eco round fight, retake chaos",
        "mechanics": "spray control, grenades, peeking, timing",
        "visuals": "bomb plant, smoke, kill feed, scoreboard"
    },

    "BGMI": {
        "situations": "hot drop death, last zone panic, squad wipe",
        "mechanics": "looting, recoil, rotation, grenade use",
        "visuals": "map, zone, kill feed, airdrop"
    },

    "Free Fire": {
        "situations": "gloo wall spam, rush fail, sniper miss",
        "mechanics": "movement, aim drag, wall placement",
        "visuals": "gloo walls, kill feed, loot box"
    },

    "Minecraft": {
        "situations": "fall death, creeper explosion, bed lost",
        "mechanics": "building, mining, PvP hit",
        "visuals": "blocks, death screen, inventory"
    },

    "Bedwars": {
        "situations": "bed break, bridge fail, void fall",
        "mechanics": "bridging, rushing, TNT, PvP",
        "visuals": "islands, bed, void, scoreboard"
    }
}

DEFAULT_GAME = {
    "situations": "mistake, fight, fail moment",
    "mechanics": "basic gameplay actions",
    "visuals": "HUD, kill feed, gameplay screen"
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
        "temperature": 0.9
    }

    res = requests.post(url, json=data, headers=headers)

    if res.status_code != 200:
        return "API ERROR"

    return res.json()["choices"][0]["message"]["content"]

def clean(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# ---------------- SIMULATOR VALIDATOR ----------------
def simulator_check(prompt_text):
    """
    Lightweight rule filter before sending to model
    """
    banned = [
        "all enemies", "entire team", "knows", "realizes",
        "thinking", "feels", "story", "because"
    ]
    for b in banned:
        if b in prompt_text.lower():
            return False
    return True

# ---------------- PROMPT ENGINE ----------------
def generate_meme(game, idea, simulator=False):

    g = get_game(game)

    prompt = f"""
You are a REAL-TIME GAMEPLAY FRAME CAPTION ENGINE.

You describe ONLY what appears on a screen recording.

----------------------------

GAME: {game}
IDEA: {idea}

----------------------------

ABSOLUTE CORE RULES:

1. Every line must describe ONLY what is visible in a screen recording frame.
2. No game events, only frame-level visuals (what camera shows at that instant).
3. No storytelling language (no: tries, plans, realizes, accidentally, manages to).
4. No invisible knowledge (no assumptions about enemies, teams, or intentions).
5. No cinematic or narrative framing.
6. No emotions, reactions, or commentary.
7. No causal words (no: because, so, therefore, then he realizes).
8. Do NOT invent UI, stats, mechanics, or objects that are not normally visible in-game.
9. Each line = exactly one frame (one moment in time only).

----------------------------

SIMULATOR MODE RULE:

If simulator mode is ON:
You must behave like a game engine viewer.
You cannot assume anything outside camera view.

----------------------------

VALID ACTIONS ONLY:
- movement
- shooting
- missing
- UI (kill feed, HUD, death screen)
- visible enemies
- visible objects

----------------------------

STRUCTURE:

HOOK → ACTION → MISTAKE → ESCALATION → RESULT

----------------------------

OUTPUT FORMAT:

🚀 TITLE:
max 4 words

🔥 HOOK:
VISUAL: screen frame only
TEXT: 2–4 words

📋 EXECUTION:

0–3 sec:
frame action only

3–7 sec:
next frame action only

7–12 sec:
visible escalation only

12–18 sec:
final result screen only

💥 FINAL PAYOFF:
meme line only

💡 WHY IT WORKS:
fast frames + mistake + payoff

----------------------------
"""

    return call_groq(prompt)

# ---------------- UI ----------------
st.set_page_config(page_title="Vyral Meme Engine", page_icon="🎮")

st.title("🎮 Vyral Meme Engine")
st.write("Short-form gaming meme script generator")

game = st.selectbox("Game", list(GAME_LAYER.keys()))
idea = st.text_input("Enter idea")

simulator_mode = st.toggle("🧠 Simulator Mode (Strict Reality Filter)")

btn = st.button("Generate Meme Script")

if btn:
    if not idea:
        st.error("Enter idea")
    else:
        with st.spinner("Generating..."):

            if simulator_mode and not simulator_check(idea):
                st.error("Blocked by simulator: unrealistic idea detected")
            else:
                result = generate_meme(game, idea, simulator_mode)

        st.markdown("## 🚀 OUTPUT")
        st.write(clean(result))