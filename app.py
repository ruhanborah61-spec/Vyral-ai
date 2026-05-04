import streamlit as st
import requests
import re

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ Missing GROQ_API_KEY in Streamlit secrets")
    st.stop()

# ---------------- GAME KNOWLEDGE LAYER ----------------
# Only real, verified in-game elements. Nothing invented.

GAME_DATA = {
    "Valorant": {
        "ranks": ["Iron 1-3", "Bronze 1-3", "Silver 1-3", "Gold 1-3", "Platinum 1-3", "Diamond 1-3", "Ascendant 1-3", "Immortal 1-3", "Radiant"],
        "stats": ["K/D ratio", "headshot %", "ACS (Average Combat Score)", "win rate"],
        "screen_elements": ["rank screen", "scoreboard", "kill feed", "crosshair", "minimap", "agent select screen", "round timer"],
        "real_actions": ["missing shots", "hitting headshot", "planting spike", "defusing spike", "using ability", "peeking corner", "holding angle", "rotating site"],
        "forbidden": ["kill counter overlay", "engagement meter", "XP bar during match", "friend online notification during gameplay"]
    },
    "BGMI": {
        "ranks": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Crown", "Ace", "Conqueror"],
        "stats": ["K/D ratio", "damage dealt", "survival time", "top 10 finishes"],
        "screen_elements": ["rank screen", "kill feed", "damage numbers", "zone map", "inventory screen", "health bar", "boost bar"],
        "real_actions": ["looting", "zone rotation", "recoil control", "reviving teammate", "throwing grenade", "driving vehicle", "jumping from plane"],
        "forbidden": ["engagement analytics", "win rate popup mid-game", "follower count overlay"]
    },
    "Fortnite": {
        "ranks": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Elite", "Champion", "Unreal"],
        "stats": ["eliminations", "placement", "Victory Royales", "survival time"],
        "screen_elements": ["rank screen", "elimination feed", "materials counter", "storm circle map", "health and shield bars"],
        "real_actions": ["building wall", "editing structure", "box fighting", "storm rotation", "picking up weapon", "Victory Royale screen"],
        "forbidden": ["analytics overlay", "engagement counter", "fake building counter"]
    },
    "Free Fire": {
        "ranks": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Heroic", "Grandmaster"],
        "stats": ["K/D ratio", "win rate", "survival time", "headshot rate"],
        "screen_elements": ["rank screen", "kill feed", "gloo wall UI", "character skill icons", "health bar", "zone timer"],
        "real_actions": ["placing gloo wall", "using character skill", "looting", "parachuting", "reviving teammate", "final zone fight"],
        "forbidden": ["fake skill meter", "invented character stats", "engagement overlay"]
    },
    "Minecraft": {
        "ranks": ["no rank system — use days survived or challenge milestone"],
        "stats": ["days survived", "items collected", "build size", "deaths count"],
        "screen_elements": ["hotbar", "health hearts", "hunger bar", "inventory screen", "XP bar", "death screen", "coordinates"],
        "real_actions": ["mining", "building", "crafting", "fighting mob", "dying", "respawning", "opening chest"],
        "forbidden": ["rank screen", "K/D ratio", "headshot percentage"]
    },
    "Bedwars": {
        "ranks": ["Iron", "Gold", "Diamond", "Emerald", "Sapphire", "Ruby", "Crystal", "Opal", "Amethyst", "Mirror"],
        "stats": ["FKDR (Final Kill Death Ratio)", "wins", "beds broken", "final kills"],
        "screen_elements": ["scoreboard", "bed status", "resource counter", "kill feed", "death screen", "win screen"],
        "real_actions": ["breaking enemy bed", "defending own bed", "buying from shop", "rushing enemy island", "bridging", "dying to fall damage"],
        "forbidden": ["invented Bedwars mechanics", "fake resource names", "non-existent shop items"]
    }
}

def get_game_data(game):
    return GAME_DATA.get(game, {
        "ranks": ["beginner", "intermediate", "advanced"],
        "stats": ["kills", "wins", "performance"],
        "screen_elements": ["scoreboard", "health bar", "gameplay footage"],
        "real_actions": ["basic gameplay actions"],
        "forbidden": ["invented mechanics"]
    })

# ---------------- API ----------------

def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen/qwen3-32b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6
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

# ---------------- VALIDATION ----------------

def validate_output(text, game):
    """Check if output contains forbidden elements for this game"""
    gd = get_game_data(game)
    forbidden = gd.get("forbidden", [])
    warnings = []
    for item in forbidden:
        if item.lower() in text.lower():
            warnings.append(f"⚠️ Possible hallucination detected: '{item}'")
    return warnings

# ---------------- MASTER PROMPT ----------------

def get_ai_suggestions(name, followers, engagement, game, platform, style, about, feedback=""):
    gd = get_game_data(game)
    feedback_text = f"\nUSER FEEDBACK: {feedback}\nGenerate a completely different idea.\n" if feedback else ""

    prompt = f"""
You are a STRICT viral gaming video script generator.

YOUR ONLY JOB: Describe exactly what appears on screen, frame by frame.

ABSOLUTE RULES — VIOLATION = FAILURE:
- ONLY describe what is VISIBLE on a screen recording
- ZERO storytelling, emotions, or narration
- ZERO invented mechanics, fake stats, or impossible UI
- ZERO cinematic language ("dramatic zoom", "intense moment")
- EACH STEP = ONE visible screen frame only
- Use ONLY the game elements listed below

CREATOR:
Name: {name}
Game: {game}
Platform: {platform}
Style: {style}
Followers: {followers}
Engagement: {engagement}%
About: {about}

VERIFIED {game.upper()} ELEMENTS — USE ONLY THESE:
Real ranks: {', '.join(gd['ranks'])}
Real stats: {', '.join(gd['stats'])}
Real screen elements: {', '.join(gd['screen_elements'])}
Real in-game actions: {', '.join(gd['real_actions'])}
FORBIDDEN (never use): {', '.join(gd['forbidden'])}

HOOK TEMPLATES — PICK EXACTLY ONE:
- "Same player. Different result."
- "X days changed everything"
- "This shouldn't be possible"
- "I tested this for X days"

CTA OPTIONS — PICK EXACTLY ONE:
- "Comment your rank"
- "Most players miss this"

OUTPUT FORMAT — RETURN EXACTLY THIS — NO THINKING TAGS — NO EXTRA TEXT:

PROBLEM:
one sentence using {name}'s exact follower and engagement numbers

TITLE:
contrast title using ONLY real {game} ranks or stats

HOOK:
exact 2-second spoken line using one hook template above
exact screen visible at this moment using only real screen elements

STEP 1:
screen cut type + exactly what is visible on screen

STEP 2:
screen cut type + exactly what is visible on screen

STEP 3:
screen cut type + exactly what is visible on screen

STEP 4:
screen cut type + exactly what is visible on screen

STEP 5:
screen cut type + exact ending line spoken + CTA from options above

POST TIME:
Platform: {platform}
Time: between 7PM and 9PM

WHY IT WORKS:
one sentence — psychology only, no hype

AVOID:
two specific things that will kill reach on {platform}

{feedback_text}
"""
    return call_groq(prompt)

def score_post(name, post_idea, followers):
    prompt = f"""
You are a strict viral content analyst. No thinking tags. Direct output only.

Creator: {name}
Followers: {followers}
Post idea: {post_idea}

RETURN EXACTLY THIS:

HOOK SCORE: X/100
SHAREABILITY: X/100
TREND MATCH: X/100
AUDIENCE FIT: X/100

WEAKNESS: one line
FIX: one action
VERDICT: POST IT or DONT POST or FIX FIRST
"""
    return call_groq(prompt)

# ---------------- PARSER ----------------

def parse_sections(text):
    text = clean_response(text)
    keys = [
        "PROBLEM", "TITLE", "HOOK",
        "STEP 1", "STEP 2", "STEP 3", "STEP 4", "STEP 5",
        "POST TIME", "WHY IT WORKS", "AVOID"
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
st.write("AI content coach for gaming creators")

st.info("👋 Fill in your details in the sidebar and click **Analyze** to get your video strategy!")

st.sidebar.header("Your Profile")

name = st.sidebar.text_input("Your name")
followers = st.sidebar.number_input("Followers", min_value=0)
likes = st.sidebar.number_input("Avg likes per post", min_value=0)

game = st.sidebar.selectbox("Your game", [
    "Valorant", "BGMI", "Fortnite",
    "Free Fire", "COD", "Minecraft", "Bedwars", "Other"
])
if game == "Other":
    game = st.sidebar.text_input("Which game?")

platform = st.sidebar.selectbox("Where do you post?", [
    "YouTube Shorts", "Instagram Reels", "TikTok"
])

style = st.sidebar.selectbox("Your content style", [
    "Teaching (tips & tricks)",
    "Meme & Comedy",
    "Clutch moments & highlights",
    "Rank up journey",
    "Reaction & commentary",
    "Other"
])
if style == "Other":
    style = st.sidebar.text_input("Describe your style")

about = st.sidebar.text_area("About you (optional)",
    placeholder="e.g. Silver ranked Valorant player trying to reach Platinum...")

analyze = st.sidebar.button("⚡ Analyze my profile")

st.sidebar.divider()
st.sidebar.subheader("🎯 Score my post idea")
post_idea = st.sidebar.text_area("Describe your post idea")
score_btn = st.sidebar.button("Score it")

# ---------------- LOGIC ----------------

if analyze:
    if followers == 0:
        st.error("Please enter your follower count!")
    elif not name:
        st.error("Please enter your name!")
    else:
        engagement = round((likes / followers) * 100, 2) if followers > 0 else 0
        st.session_state.engagement = engagement
        st.session_state.name = name
        st.session_state.game = game
        with st.spinner("Analyzing your profile..."):
            st.session_state.result = get_ai_suggestions(
                name, followers, engagement,
                game, platform, style, about
            )

if "result" in st.session_state:
    engagement = st.session_state.engagement
    creator_name = st.session_state.name
    current_game = st.session_state.get("game", "Valorant")

    st.subheader(f"📊 {creator_name}'s Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Engagement Rate", f"{engagement}%")
    with col2:
        if followers < 1000:
            if engagement > 8:
                st.success("Excellent! Top tier for your size 🔥")
            elif engagement > 4:
                st.info("Good! Above average 👍")
            else:
                st.warning("Needs improvement!")
        elif followers < 10000:
            if engagement > 5:
                st.success("Excellent! Top tier 🔥")
            elif engagement > 2:
                st.info("Good! Above average 👍")
            else:
                st.warning("Needs improvement!")
        else:
            if engagement > 3:
                st.success("Excellent! Top tier 🔥")
            elif engagement > 1:
                st.info("Good! Above average 👍")
            else:
                st.warning("Needs improvement!")

    sections = parse_sections(st.session_state.result)

    # Validate output for hallucinations
    warnings = validate_output(st.session_state.result, current_game)
    if warnings:
        for w in warnings:
            st.error(w)

    st.divider()

    if sections["PROBLEM"]:
        st.subheader("⚠️ Your Growth Problem")
        st.warning(sections["PROBLEM"])

    if sections["TITLE"]:
        st.subheader("🎬 Video Title")
        st.info(sections["TITLE"])

    if sections["HOOK"]:
        st.subheader("🔥 Hook (0-2 sec)")
        st.warning(sections["HOOK"])

    steps_exist = any(sections[f"STEP {i}"] for i in range(1, 6))
    if steps_exist:
        st.subheader("📋 Execution Steps")
        for i in range(1, 6):
            step = sections[f"STEP {i}"]
            if step:
                st.markdown(f"**Step {i}:** {step}")

    if sections["POST TIME"]:
        st.subheader("🕐 When to Post")
        st.success(sections["POST TIME"])

    if sections["WHY IT WORKS"]:
        st.subheader("💡 Why It Works")
        st.write(sections["WHY IT WORKS"])

    if sections["AVOID"]:
        st.subheader("❌ What to Avoid")
        st.write(sections["AVOID"])

    st.divider()
    st.caption("Come back after posting — I'll fix your next video 🎮")

    st.subheader("💬 Not happy with this idea?")
    feedback = st.text_input("Tell us why")
    regenerate = st.button("🔄 Regenerate")

    if regenerate and feedback:
        with st.spinner("Generating better idea..."):
            st.session_state.result = get_ai_suggestions(
                name, followers, engagement,
                game, platform, style, about, feedback
            )
        st.rerun()

if score_btn and post_idea:
    with st.spinner("Scoring your idea..."):
        score_result = score_post(name, post_idea, followers)
    score_result = clean_response(score_result)
    st.divider()
    st.subheader("📊 Post Score Report")
    lines = score_result.split('\n')
    for line in lines:
        if any(x in line.upper() for x in ['HOOK SCORE', 'SHAREABILITY', 'TREND MATCH', 'AUDIENCE FIT']):
            parts = line.split(':')
            if len(parts) == 2:
                st.metric(parts[0].strip(), parts[1].strip())
        elif 'VERDICT' in line.upper():
            st.subheader(line)
        elif line.strip():
            st.write(line)
