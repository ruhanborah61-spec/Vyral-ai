import streamlit as st
import requests
import re

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ Missing GROQ_API_KEY in Streamlit secrets")
    st.stop()

def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen/qwen3-32b",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return f"API Error: {response.text}"
    result = response.json()["choices"][0]["message"]["content"]
    if not result:
        return "API returned empty response. Please try again."
    return result

def clean_response(text):
    # Remove <think>...</think> blocks completely
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return text.strip()

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
            pattern = key + ":"
            if line.upper().startswith(pattern):
                current = key
                content = line[len(pattern):].strip()
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

# ---------------- AI FUNCTIONS ----------------

def get_ai_suggestions(name, followers, engagement, game, platform, style, about, feedback=""):
    feedback_text = f"\nUSER FEEDBACK: {feedback}\nGenerate a completely different idea that fixes this.\n" if feedback else ""

    prompt = f"""
You are a viral gaming content coach who has studied 10 million viral gaming videos.

THIS CREATOR MAKES GAMING VIDEOS ABOUT {game}.
Their content is ONLY about gameplay — kills, ranks, aim, strategies.
NOT about social media growth or analytics.
ALL visuals must come from INSIDE the game.

CREATOR:
Name: {name}
Game: {game}
Platform: {platform}
Style: {style}
About: {about}
Followers: {followers}
Engagement: {engagement}%

YOUR JOB:
Give ONE video idea that will get maximum views on {platform}.
The idea must be simple enough for a beginner creator to film with just their phone.

RULES:
1. Show contrast or proof in the FIRST 2 seconds — never delay
2. Hook must use ONE of: "This shouldn't be possible", "Same player. Different result.", "X days changed everything", "I tested this for X days"
3. NEVER use: "secret trick", "hack", "link in bio", "something changed", "I was struggling"
4. Every step must have a camera direction: fast zoom, cut to, text overlay, split screen, freeze frame
5. Before/after comparison is MANDATORY
6. CTA must be: "Comment your rank" or "Most players miss this" — never "follow for part 2"
7. Time must be between 7PM and 9PM
8. Do NOT show face, room, or real camera.
9. ALL visuals must be from inside the game UI or gameplay.
10. All visuals must be from inside {game} — scoreboard, rank screen, kill feed, gameplay footage
11. NEVER suggest analytics graphs, engagement metrics, or social media tools as visuals
12. Keep steps simple — one action per step
13. Do NOT use brackets [] in your output — write real specific actions

RETURN EXACTLY THIS FORMAT — NO EXTRA TEXT — NO THINKING — JUST THE OUTPUT:

PROBLEM:
one brutal sentence using exact follower count and engagement numbers

TITLE:
scroll stopping title using contrast like "X → Y same player"

HOOK:
exact words to say in first 2 seconds
exact visual from inside the game

STEP 1:
camera direction + exact action

STEP 2:
camera direction + exact action

STEP 3:
camera direction + exact action

STEP 4:
camera direction + exact action

STEP 5:
camera direction + exact ending line + CTA

POST TIME:
Platform: {platform}
Time: between 7PM and 9PM

WHY IT WORKS:
one simple sentence

AVOID:
AVOID must be specific to THIS idea.
Do NOT give generic advice like “don’t show face” or “avoid low quality”.
Each point must describe a mistake that would directly reduce views or trust in THIS exact video.

{feedback_text}
"""
    return call_groq(prompt)

def score_post(name, post_idea, followers):
    prompt = f"""
You are a strict viral content analyst for gaming videos.
Be direct. No generic feedback.

Creator: {name}
Followers: {followers}
Post idea: {post_idea}

RETURN EXACTLY THIS FORMAT — NO THINKING — JUST THE OUTPUT:

HOOK SCORE: X/100
SHAREABILITY: X/100
TREND MATCH: X/100
AUDIENCE FIT: X/100

WEAKNESS: one specific line
FIX: one exact action
VERDICT: POST IT or DONT POST or FIX FIRST
"""
    return call_groq(prompt)

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