import streamlit as st
import requests
import re

# ---------------- API ----------------
API_KEY = st.secrets["GROQ_API_KEY"]

if not API_KEY:
    st.error("Missing API Key")
    st.stop()

# ---------------- GAME LAYER (SAFE ONLY) ----------------
GAME_LAYER = {
    "Valorant": ["move", "shoot", "peek", "reload", "plant spike", "defuse"],
    "CS2": ["shoot", "smoke", "flash", "plant bomb", "defuse", "peek"],
    "BGMI": ["loot", "shoot", "drive", "revive", "crouch"],
    "Free Fire": ["shoot", "jump", "gloo wall", "revive"],
    "Minecraft": ["mine", "place block", "fall", "hit mob", "die"],
    "Bedwars": ["bridge", "hit", "break bed", "fall void"]
}

# ---------------- API CALL ----------------
def call_llm(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "qwen/qwen3-32b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    res = requests.post(url, json=data, headers=headers)

    if res.status_code != 200:
        return "API ERROR"

    return res.json()["choices"][0]["message"]["content"]

# ---------------- STRICT VALIDATOR ----------------
def clean_output(text):
    banned = [
        "emotion", "feels", "realizes", "story", "cinematic",
        "health bar", "damage counter", "thinking", "accidentally"
    ]
    for b in banned:
        text = re.sub(b, "", text, flags=re.IGNORECASE)
    return text.strip()

# ---------------- PROMPT ENGINE ----------------
def generate(game, idea):

    allowed_actions = ", ".join(GAME_LAYER.get(game, []))

    prompt = f"""
You are a STRICT GAMEPLAY FRAME ENGINE.

RULES:
- ONLY visible screen actions
- NO storytelling
- NO emotions
- NO imagination
- NO fake UI or stats
- EACH LINE = ONE FRAME ONLY

GAME: {game}
ALLOWED ACTIONS: {allowed_actions}

IDEA: {idea}

OUTPUT FORMAT:

TITLE: max 5 words

HOOK:
visible frame only

FRAME 1:
only visible action

FRAME 2:
only visible action

FRAME 3:
only visible action

RESULT:
final screen state

WHY IT WORKS:
mistake → escalation → payoff
"""

    return clean_output(call_llm(prompt))

# ---------------- UI ----------------
st.set_page_config(page_title="Vyral V3", page_icon="🎮")

st.title("🎮 VYRAL ENGINE V3 (FINAL)")

game = st.selectbox("Game", list(GAME_LAYER.keys()))
idea = st.text_input("Enter idea")

if st.button("Generate"):
    if idea:
        st.markdown("## 🚀 OUTPUT")
        st.write(generate(game, idea))