import streamlit as st
import requests
import re

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ Missing GROQ_API_KEY in Streamlit secrets")
    st.stop()

# ---------------- GAME KNOWLEDGE LAYER ----------------
GAME_KNOWLEDGE = {
    "Valorant": {
        "ranks": "Iron, Bronze, Silver, Gold, Platinum, Diamond, Ascendant, Immortal, Radiant",
        "stats": "K/D ratio, headshot percentage, win rate, ACS (Average Combat Score)",
        "mechanics": "crosshair placement, pre-aiming, peeking, spray control, ability usage, site control, rotation",
        "visuals": "rank screen, scoreboard, kill feed, minimap, crosshair, agent select screen",
        "content_hooks": "rank up journey, aim improvement, crosshair tips, agent guides, clutch moments"
    },
    "BGMI": {
        "ranks": "Bronze, Silver, Gold, Platinum, Diamond, Crown, Ace, Conqueror",
        "stats": "K/D ratio, damage per match, survival time, win rate",
        "mechanics": "drop location, looting, zone rotation, recoil control, vehicle usage, compound strategy",
        "visuals": "rank screen, kill feed, damage numbers, zone map, inventory screen",
        "content_hooks": "hot drop survival, recoil control, zone strategy, Conqueror push"
    },
    "Fortnite": {
        "ranks": "Bronze, Silver, Gold, Platinum, Diamond, Elite, Champion, Unreal",
        "stats": "eliminations, placement, survival time, Victory Royales",
        "mechanics": "building, editing, box fighting, zone rotation, weapon selection, storm strategy",
        "visuals": "rank screen, elimination feed, building materials count, storm circle map",
        "content_hooks": "zero build tips, edit course, box fight, Victory Royale run"
    },
    "FIFA": {
        "ranks": "Division 10 to Division 1, Elite Division",
        "stats": "win rate, goals scored, clean sheets, pass accuracy",
        "mechanics": "skill moves, defensive positioning, finesse shots, set pieces, player chemistry",
        "visuals": "division rank screen, match result screen, player stats card, goal replay",
        "content_hooks": "rank up from Division 5, skill move tutorials, best meta players, comeback wins"
    },
    "Free Fire": {
        "ranks": "Bronze, Silver, Gold, Platinum, Diamond, Heroic, Grandmaster",
        "stats": "K/D ratio, win rate, survival time, headshot rate",
        "mechanics": "drop zone, gloo wall usage, character skills, rotation, final zone strategy",
        "visuals": "rank screen, kill feed, gloo wall placement, character skill screen",
        "content_hooks": "Grandmaster push, gloo wall tricks, character skill combos, hot drop survival"
    },
    "COD": {
        "ranks": "Bronze, Silver, Gold, Platinum, Diamond, Crimson, Iridescent, Top 250",
        "stats": "K/D ratio, win rate, damage per game, headshot percentage",
        "mechanics": "slide cancel, movement, sniper quick scope, SMG rushing, hardpoint rotation",
        "visuals": "rank screen, kill feed, scorestreak screen, damage numbers",
        "content_hooks": "rank up journey, movement tips, best loadout, clutch moments"
    },
    "Minecraft": {
        "ranks": "no rank system — use subscriber milestones or challenge completion",
        "stats": "build time, survival days, challenge completion",
        "mechanics": "redstone, speedrun techniques, building, survival strategies, PvP",
        "visuals": "build before/after, speedrun timer, inventory, death screen",
        "content_hooks": "speedrun, 100 days challenge, build transformation, survival tips"
    }
}

def get_game_info(game):
    return GAME_KNOWLEDGE.get(game, {
        "ranks": "beginner to advanced",
        "stats": "kills, wins, performance metrics",
        "mechanics": "basic gameplay mechanics",
        "visuals": "gameplay footage, score screen",
        "content_hooks": "improvement journey, tips and tricks"
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
        "temperature": 0.7
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

# ---------------- MASTER PROMPT ----------------

def get_ai_suggestions(name, followers, engagement, game, platform, style, about, feedback=""):
    game_info = get_game_info(game)
    feedback_text = f"\nUSER FEEDBACK: {feedback}\nGenerate a completely different idea that fixes this.\n" if feedback else ""

    prompt = f"""
You are a viral gaming content coach specializing in short-form video strategy.

CREATOR PROFILE:
Name: {name}
Game: {game}
Platform: {platform}
Style: {style}
About: {about}
Followers: {followers}
Engagement: {engagement}%

REAL {game.upper()} KNOWLEDGE — USE ONLY THESE:
Ranks: {game_info['ranks']}
Stats: {game_info['stats']}
Mechanics: {game_info['mechanics']}
Valid visuals: {game_info['visuals']}
Proven content hooks: {game_info['content_hooks']}

STRICT RULES:
1. ONLY use ranks, stats, mechanics and visuals from the list above — never invent terms
2. Show contrast or proof in first 2 seconds
3. Hook must use ONE of: "Same player. Different result." / "X days changed everything" / "This shouldn't be possible" / "I tested this for X days"
4. NEVER use: secret trick, hack, link in bio, something changed, I was struggling
5. Every step needs ONE camera direction: fast zoom / cut to / text overlay / split screen / freeze frame
6. Before/after comparison is mandatory
7. CTA must be: "Comment your rank" or "Most players miss this"
8. Post time between 7PM-9PM only
9. All visuals must be from inside the game
10. Do NOT use brackets in output — write real specific actions
11. Keep each step to ONE simple action a beginner can film with a phone

OUTPUT FORMAT — RETURN EXACTLY THIS — NO THINKING — NO EXTRA TEXT:

PROBLEM:
[one brutal sentence using {name}'s exact numbers]

TITLE:
[contrast title using real {game} ranks or stats — example: "Silver → Gold. Same player. 7 days."]

HOOK:
[exact words to say]
[exact in-game visual using only valid visuals listed above]

STEP 1:
[camera direction + exact in-game action]

STEP 2:
[camera direction + exact in-game action]

STEP 3:
[camera direction + exact in-game action]

STEP 4:
[camera direction + exact in-game action]

STEP 5:
[camera direction + ending line + CTA]

POST TIME:
Platform: {platform}
Time: [7PM-9PM]

WHY IT WORKS:
[one sentence explaining the psychology]

AVOID:
[two specific things]

{feedback_text}
"""
    return call_groq(prompt)

def score_post(name, post_idea, followers):
    prompt = f"""
You are a strict viral content analyst for gaming videos.
Be direct. No generic feedback. No thinking tags.

Creator: {name}
Followers: {followers}
Post idea: {post_idea}

RETURN EXACTLY THIS FORMAT:

HOOK SCORE: X/100
SHAREABILITY: X/100
TREND MATCH: X/100
AUDIENCE FIT: X/100

WEAKNESS: one specific line
FIX: one exact action
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
    "FIFA", "Free Fire", "COD", "Minecraft", "Other"
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
        with st.spinner("Analyzing your profile..."):
            st.session_state.result = get_ai_suggestions(
                name, followers, engagement,
                game, platform, style, about
            )

if "result" in st.session_state:
    engagement = st.session_state.engagement
    creator_name = st.session_state.name

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