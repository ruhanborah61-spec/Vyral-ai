import streamlit as st
import requests

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
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return f"API Error: {response.text}"
    result = response.json()["choices"][0]["message"]["content"]
    if not result:
        return "API returned empty response. Please try again."
    return result

# ---------------- AI FUNCTIONS ----------------

def get_ai_suggestions(name, followers, engagement, game, platform, style, about, feedback=""):
    feedback_text = f"\nUSER FEEDBACK:\n{feedback}\nGenerate a completely different idea.\n" if feedback else ""

    prompt = f"""
You are an elite viral gaming content coach.
You have studied 10 million viral gaming videos.
You know exactly what stops scroll and what gets ignored.

CREATOR PROFILE:
Name: {name}
Game: {game}
Platform: {platform}
Content Style: {style}
About: {about}
Followers: {followers}
Engagement: {engagement}%

GAMING RULES:
- Focus ONLY on: skill improvement, rank up, mistakes, before/after proof
- NEVER suggest: product downloads, live streams, random game recommendations
- Every idea must follow: contrast → mystery → quick reveal format
- Every step MUST include a camera direction: fast zoom, cut to, slow zoom, split screen, text overlay, freeze frame
- Example: "0-2 sec: Fast zoom on scoreboard showing 20% headshot ratio"
- Example: "2-5 sec: Cut to gameplay clip of missed shots"
- Example: "10-15 sec: Freeze frame on kill count then text overlay 'same player'"
- NEVER use filler phrases like: "something changed", "I was struggling", "want to know how"
- NEVER use "secret trick" or "hack" — sounds like clickbait
- NEVER delay the strongest visual — show contrast or proof in first 2 seconds
- Hook must show CONTRAST or IMPOSSIBILITY — not narration
- Use believable numbers with clear before/after
- Visual must always be from INSIDE the game — scoreboard, rank screen, kill feed
- NEVER suggest engagement graphs, analytics tools, or external apps as visuals
- Example visual: "Fast zoom on Valorant rank screen" or "Split screen of kill counts"
- Every idea MUST include split screen or side by side comparison
- Content must be phone recordable only
- NEVER use "link in bio" as CTA
- Time MUST be between 7PM-9PM only

HOOK TEMPLATES — USE ONE OF THESE STYLES:
- "This shouldn't be possible…" (show proof instantly)
- "Same player. Different result." (show contrast)
- "X days changed everything" (show before/after)
- "I tested this for X days…" (show tracked result)

STYLE RULES:
- Teaching: measurable improvement, before/after, one specific fix
- Meme & Comedy: relatable fails, unexpected twist, humor
- Clutch moments: highlight reels, insane plays, reaction hook
- Rank up journey: day by day tracking, visible progress
- Reaction: surprising moment, commentary hook

PROBLEM DIAGNOSIS RULES:
- Be brutal and specific — use their exact numbers
- Never say "not making an impact" — say what's actually wrong
- Example: "You're not converting viewers into interaction" not "struggling to grow"

CTA RULES — PICK ONE:
- "Comment your [stat]" (drives engagement)
- "I'll show the exact fix tomorrow" (curiosity loop)
- "Most players never fix this" (ego trigger)
- NEVER use "link in bio" or "follow for part 2" without strong Part 1

RETURN EXACTLY THIS FORMAT — NO BRACKETS — NO EXTRA TEXT:

PROBLEM:
brutal specific diagnosis using exact follower count and engagement numbers

TITLE:
scroll stopping title using contrast format like "X → Y same player"

HOOK (0-2 sec):
exact words using one of the hook templates above
exact visual showing contrast or proof instantly — phone recordable

STEPS:
0-2 sec: show split screen or contrast visual instantly
2-5 sec: exact text overlay or what creator says
5-10 sec: show bad clip or before moment
10-15 sec: show improved clip or after moment
15-20 sec: quick hint of fix without full explanation then exact CTA

POST AT:
Platform: {platform}
Time: between 7PM-9PM

WHY IT WORKS:
one line explaining the psychology

AVOID:
two specific things that would kill this video

{feedback_text}
"""
    return call_groq(prompt)

def score_post(name, post_idea, followers):
    prompt = f"""
You are a strict viral content analyst for gaming creators.
Be brutal and specific. No generic feedback.

Creator: {name}
Followers: {followers}
Post idea: {post_idea}

RETURN EXACTLY THIS FORMAT — NO BRACKETS:

HOOK SCORE: X/100
SHAREABILITY: X/100
TREND MATCH: X/100
AUDIENCE FIT: X/100

WEAKNESS:
one specific line — what will kill this video

FIX:
one exact action to improve it

VERDICT: POST IT ✅ or DON'T POST ❌ or FIX FIRST ⚠️
"""
    return call_groq(prompt)

def parse_sections(text):
    sections = {
        "PROBLEM": "",
        "TITLE": "",
        "HOOK": "",
        "STEPS": "",
        "POST AT": "",
        "WHY IT WORKS": "",
        "AVOID": ""
    }
    current = None
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        matched = False
        for key in sections:
            if line.startswith(key + ":") or line == key + ":":
                current = key
                content = line[len(key)+1:].strip()
                if content:
                    sections[key] = content
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

st.info("👋 Enter your details in the sidebar and click **Analyze** to get your personalized content strategy!")

# SIDEBAR
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

    if sections["STEPS"]:
        st.subheader("📋 Execution Steps")
        st.code(sections["STEPS"])

    if sections["POST AT"]:
        st.subheader("🕐 When to Post")
        st.success(sections["POST AT"])

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
    st.divider()
    st.subheader("📊 Post Score Report")

    lines = score_result.split('\n')
    for line in lines:
        if 'SCORE:' in line or 'SHAREABILITY:' in line or 'TREND' in line or 'AUDIENCE' in line:
            st.metric(line.split(':')[0].strip(), line.split(':')[1].strip() if ':' in line else "")
        elif 'VERDICT' in line:
            st.subheader(line)
        elif line.strip():
            st.write(line)