import streamlit as st
import requests
import re

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ Missing GROQ_API_KEY in Streamlit secrets")
    st.stop()

# ---------------- GAME KNOWLEDGE ----------------

GAME_DATA = {
    "Valorant": {
        "ranks": ["Iron 1-3", "Bronze 1-3", "Silver 1-3", "Gold 1-3", "Platinum 1-3", "Diamond 1-3", "Ascendant 1-3", "Immortal 1-3", "Radiant"],
        "screen_elements": ["scoreboard", "kill feed", "crosshair", "minimap", "rank screen", "death screen", "spike timer", "round timer", "ACS", "headshot %"],
        "relatable_situations": [
            "missing an easy shot", "dying to a Silver player", "teammates not rotating",
            "spike planted wrong site", "running out of credits", "getting one-tapped",
            "losing a 1v1 you should win", "trolling teammate", "losing streak", "clutching and losing next round"
        ],
        "meme_reactions": ["facepalm", "disbelief", "rage quit moment", "unexpected win", "carried by teammate"]
    },
    "BGMI": {
        "ranks": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Crown", "Ace", "Conqueror"],
        "screen_elements": ["kill feed", "damage numbers", "zone map", "health bar", "boost bar", "rank screen", "death screen", "inventory"],
        "relatable_situations": [
            "dying in final zone", "getting thirsted after knock", "looting the whole game and dying early",
            "teammate stealing kill", "missing a shot at close range", "vehicle exploding",
            "running out of ammo in fight", "getting hit by pan", "dying to zone"
        ],
        "meme_reactions": ["rage moment", "disbelief", "unexpected third party", "clutch fail", "lucky win"]
    },
    "Free Fire": {
        "ranks": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Heroic", "Grandmaster"],
        "screen_elements": ["kill feed", "health bar", "gloo wall UI", "character skill icons", "rank screen", "zone timer", "death screen"],
        "relatable_situations": [
            "gloo wall not working", "dying to gloo wall camper", "character skill failing",
            "hot drop death", "teammate revive ignored", "missing shots at close range",
            "dying to final zone", "getting knocked by random"
        ],
        "meme_reactions": ["disbelief", "rage", "clutch moment fail", "lucky escape", "unexpected death"]
    },
    "Minecraft": {
        "ranks": ["Day 1", "Day 10", "Day 100"],
        "screen_elements": ["health hearts", "hunger bar", "hotbar", "inventory", "XP bar", "death screen", "coordinates", "crafting table UI"],
        "relatable_situations": [
            "dying to creeper", "falling into lava", "losing diamonds", "skeleton shooting from dark",
            "forgetting to eat", "dying on day 99 of 100 days", "getting lost in caves",
            "bed not set", "respawning far from base"
        ],
        "meme_reactions": ["screaming internally", "everything is fine then dies", "unexpected creeper", "clutch escape"]
    },
    "Bedwars": {
        "ranks": ["Iron", "Gold", "Diamond", "Emerald", "Sapphire", "Ruby", "Crystal", "Opal", "Amethyst", "Mirror"],
        "screen_elements": ["scoreboard", "bed status icons", "resource counter", "kill feed", "death screen", "win screen", "shop UI"],
        "relatable_situations": [
            "bed broken while defending", "dying to void", "enemy rushing with fireball",
            "forgetting to protect bed", "getting spawn killed", "running out of resources",
            "teammate leaving mid game", "winning with 1 heart"
        ],
        "meme_reactions": ["betrayal feeling", "panic mode", "clutch win", "unexpected loss", "rage"]
    },
    "CS2": {
        "ranks": ["Silver 1-4", "Silver Elite", "Gold Nova 1-4", "Master Guardian 1-2", "Legendary Eagle", "Supreme", "Global Elite"],
        "screen_elements": ["scoreboard", "kill feed", "crosshair", "radar", "money display", "health bar", "rank screen", "death cam"],
        "relatable_situations": [
            "missing a shot at point blank", "buying wrong weapon", "teammate blocking shot",
            "falling off ledge", "bomb timer panic", "running out of bullets in fight",
            "getting headshot through smoke", "losing pistol round", "eco round fail"
        ],
        "meme_reactions": ["disbelief", "teammate blame", "clutch choke", "unexpected win", "rank anxiety"]
    }
}

def get_game_data(game):
    return GAME_DATA.get(game, {
        "ranks": ["beginner", "intermediate", "advanced"],
        "screen_elements": ["scoreboard", "health bar", "kill feed"],
        "relatable_situations": ["missing shots", "dying unexpectedly", "losing a close game"],
        "meme_reactions": ["disbelief", "rage", "unexpected moment"]
    })

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
        "temperature": 0.65
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return f"API Error: {response.text}"
    result = response.json()["choices"][0]["message"]["content"]
    if not result:
        return "API returned empty response. Please try again."
    return result

def clean_response(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return text.strip()

# ---------------- MEME PROMPT ----------------

def get_meme_script(name, game, rank, platform, situation, feedback=""):
    gd = get_game_data(game)
    feedback_text = f"\nUSER FEEDBACK: {feedback}\nGenerate a completely different meme idea.\n" if feedback else ""

    prompt = f"""
You are a viral gaming meme script generator.
You write short-form meme scripts that gamers can open OBS and record immediately.

CREATOR:
Name: {name}
Game: {game}
Rank: {rank}
Platform: {platform}
Situation: {situation}

VERIFIED {game.upper()} ELEMENTS — USE ONLY THESE:
Ranks: {', '.join(gd['ranks'])}
Real screen elements: {', '.join(gd['screen_elements'])}
Relatable situations: {', '.join(gd['relatable_situations'])}
Meme reactions: {', '.join(gd['meme_reactions'])}

MEME SCRIPT RULES:
1. Every frame = one visible screen moment only
2. Zero storytelling, zero narration, zero emotions described
3. Only describe what is VISIBLE on screen
4. Maximum 6 frames total
5. Each frame must be recordable from real gameplay
6. Text overlays must be short — maximum 5 words
7. Use only real screen elements listed above
8. Meme must be relatable to ANY player at {rank} rank
9. Pacing: fast cuts — each frame maximum 3 seconds
10. NEVER invent fake UI, fake stats, or impossible actions
11. NO thinking tags in output
12. NEVER use face cam, reactions, or anything outside the game screen
13. NEVER create UI elements that don't exist in the game
14. Every frame must exist naturally during real gameplay — no custom setups

MEME FORMATS — PICK ONE THAT FITS:
- "Me vs the game" (player expectation vs reality)
- "Every [rank] player ever" (relatable rank behavior)
- "POV: [situation]" (point of view meme)
- "When [thing happens]" (reaction meme)
- "Day X of [challenge]" (progress meme)

OUTPUT FORMAT — RETURN EXACTLY THIS — NO EXTRA TEXT:

MEME TITLE:
one punchy meme title using the format above

MEME TYPE:
which format you picked and why in one line

FRAME 1:
exact screen element visible + text overlay if needed

FRAME 2:
exact screen element visible + text overlay if needed

FRAME 3:
exact screen element visible + text overlay if needed

FRAME 4:
exact screen element visible + text overlay if needed

FRAME 5:
exact screen element visible + text overlay if needed

FRAME 6:
exact screen element visible + final text overlay + CTA

POST TIME:
Platform: {platform}
Time: between 7PM and 9PM

WHY IT WORKS:
one sentence — what makes this relatable

{feedback_text}
"""
    return call_groq(prompt)

def score_post(name, post_idea, game):
    prompt = f"""
You are a strict viral gaming meme analyst. No thinking tags. Direct output only.

Creator: {name}
Game: {game}
Meme idea: {post_idea}

RETURN EXACTLY THIS:

RELATABILITY: X/100
HUMOR SCORE: X/100
SHAREABILITY: X/100
RECORD EASE: X/100

WEAKNESS: one line
FIX: one action
VERDICT: POST IT or DONT POST or FIX FIRST
"""
    return call_groq(prompt)

# ---------------- PARSER ----------------

def parse_sections(text):
    text = clean_response(text)
    keys = [
        "MEME TITLE", "MEME TYPE",
        "FRAME 1", "FRAME 2", "FRAME 3",
        "FRAME 4", "FRAME 5", "FRAME 6",
        "POST TIME", "WHY IT WORKS"
    ]
    sections = {k: "" for k in keys}
    current = None

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        matched = False
        for key in keys:
            if line.upper().startswith(key + ":"):
                current = key
                content = line[len(key)+1:].strip()
                if content:
                    sections[key] = content
                matched = True
                break
            elif line.upper() == key:
                current = key
                matched = True
                break
        if not matched and current:
            if sections[current]:
                sections[current] += "\n" + line
            else:
                sections[current] = line

    return sections

# ---------------- UI ----------------

st.set_page_config(page_title="Vyral", page_icon="🎮")

st.title("Vyral 🎮")
st.write("Gaming meme script generator — open OBS and record")

st.info("👋 Fill in your details and get a ready-to-record meme script in seconds!")

st.sidebar.header("Your Profile")

name = st.sidebar.text_input("Your name")

game = st.sidebar.selectbox("Your game", [
    "Valorant", "BGMI", "Free Fire",
    "Minecraft", "Bedwars", "CS2"
])

gd = get_game_data(game)
rank = st.sidebar.selectbox("Your current rank", gd["ranks"])

platform = st.sidebar.selectbox("Where do you post?", [
    "YouTube Shorts", "Instagram Reels", "TikTok"
])

situation = st.sidebar.selectbox(
    "Pick a relatable situation",
    gd["relatable_situations"]
)

generate = st.sidebar.button("🎮 Generate Meme Script")

st.sidebar.divider()
st.sidebar.subheader("🎯 Score my meme idea")
meme_idea = st.sidebar.text_area("Describe your meme idea")
score_btn = st.sidebar.button("Score it")

# ---------------- LOGIC ----------------

if generate:
    if not name:
        st.error("Please enter your name!")
    else:
        st.session_state.name = name
        st.session_state.game = game
        with st.spinner("Generating your meme script..."):
            st.session_state.result = get_meme_script(
                name, game, rank, platform, situation
            )

if "result" in st.session_state:
    sections = parse_sections(st.session_state.result)

    st.divider()

    if sections["MEME TITLE"]:
        st.subheader("😂 Meme Title")
        st.info(sections["MEME TITLE"])

    if sections["MEME TYPE"]:
        st.caption(f"Format: {sections['MEME TYPE']}")

    frames_exist = any(sections[f"FRAME {i}"] for i in range(1, 7))
    if frames_exist:
        st.subheader("🎬 Script Frames")
        for i in range(1, 7):
            frame = sections[f"FRAME {i}"]
            if frame:
                st.markdown(f"**Frame {i}:** {frame}")

    if sections["POST TIME"]:
        st.subheader("🕐 When to Post")
        st.success(sections["POST TIME"])

    if sections["WHY IT WORKS"]:
        st.subheader("💡 Why It Works")
        st.write(sections["WHY IT WORKS"])

    st.divider()
    st.caption("Open OBS → Record exactly these frames → Post 🎮")

    st.subheader("💬 Not happy with this script?")
    feedback = st.text_input("Tell us why")
    regenerate = st.button("🔄 Regenerate")

    if regenerate and feedback:
        with st.spinner("Generating different script..."):
            st.session_state.result = get_meme_script(
                st.session_state.name,
                st.session_state.game,
                rank, platform, situation, feedback
            )
        st.rerun()

if score_btn and meme_idea:
    with st.spinner("Scoring your meme idea..."):
        score_result = score_post(
            st.session_state.get("name", "Creator"),
            meme_idea,
            st.session_state.get("game", "Valorant")
        )
    score_result = clean_response(score_result)
    st.divider()
    st.subheader("📊 Meme Score")
    lines = score_result.split('\n')
    for line in lines:
        if any(x in line.upper() for x in ['RELATABILITY', 'HUMOR', 'SHAREABILITY', 'RECORD']):
            parts = line.split(':')
            if len(parts) == 2:
                st.metric(parts[0].strip(), parts[1].strip())
        elif 'VERDICT' in line.upper():
            st.subheader(line)
        elif line.strip():
            st.write(line)