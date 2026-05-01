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
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return f"API Error: {response.text}"
    return response.json()["choices"][0]["message"]["content"]

# ---------------- AI PROMPT ENGINE ----------------

def get_ai_suggestions(name, followers, engagement, niche, content_style, challenge, target_audience, about, feedback=""):
    feedback_text = f"\nUSER FEEDBACK TO FIX:\n{feedback}\nGenerate completely different ideas addressing this concern.\n" if feedback else ""

    prompt = f"""
You are a STRICT viral content engineering system.

Your job is NOT creativity.
Your job is to DESIGN HIGH-PERFORMANCE SOCIAL MEDIA VIDEOS.

You think like:
- YouTube Shorts algorithm engineer
- TikTok retention optimizer
- Instagram Reels growth strategist

Your ONLY goal: maximize FOLLOWERS + WATCH TIME + SHARES for {name}.

---

USER DATA:
Name: {name}
About: {about}
Niche: {niche}
Content Style: {content_style}
Challenge: {challenge}
Target Audience: {target_audience}
Followers: {followers}
Engagement: {engagement}%

---

RULES:
- EXACTLY 3 ideas only
- SAME FORMAT for all ideas
- NO fluff, NO storytelling, NO motivation
- Every step MUST include 1 real-world example in simple language
- If using technical terms, explain them in brackets
- Keep timing strict: 0-2s, 0-5s, 5-15s, 15-20s
- Each idea uses a different viral trigger:
  1. Shock
  2. Curiosity
  3. Value
- Assume creator is a beginner — make every step crystal clear

{feedback_text}

---

FORMAT (DO NOT CHANGE):

{name}, your problem is [1 precise growth diagnosis].

---

Idea 1:
Title:
Platform:
Duration: 20 sec

Hook (0-2s):
Visual: [exact shot description, e.g. "close up of your face looking shocked"]
Line: [exact words to say]
Example: [real example of this hook working]

Execution:
0-5s:
Action: [exact action]
Example: [real world example]

5-15s:
Action: [exact action]
Example: [real world example]

15-20s:
Action: [exact action]
Example: [real world example]

CTA: [exact words]
Why it works: [one line]

---

Idea 2:
(SAME FORMAT)

---

Idea 3:
(SAME FORMAT)

---

FINAL CHECK:
- 3 ideas only
- no extra text
- strict format compliance
- every technical term explained in simple language
"""
    return call_groq(prompt)

# ---------------- SCORING ENGINE ----------------

def score_post(name, post_idea, followers):
    prompt = f"""
You are a strict viral content analyst.

Evaluate this post idea:

Creator: {name}
Followers: {followers}

Post:
{post_idea}

Return EXACT format:

Hook Score: /100
Shareability: /100
Trend Match: /100
Audience Fit: /100

Weakness:
Fix:
"""
    return call_groq(prompt)

# ---------------- UI ----------------

st.set_page_config(page_title="Vyral", page_icon="🚀")

st.title("Vyral 🚀")
st.write("AI Viral Content Engineer for Creators")

st.info("👋 Welcome to Vyral! Here's how to get started:")
st.markdown("""
1. Enter your details in the sidebar
2. Click **Analyze Profile**
3. Get your personalized viral content strategy
4. Use **Post Scoring** to score your next idea
""")

st.sidebar.header("Creator Profile")

name = st.sidebar.text_input("Name")
followers = st.sidebar.number_input("Followers", min_value=0)
likes = st.sidebar.number_input("Avg Likes", min_value=0)
about = st.sidebar.text_area("About You", placeholder="e.g. I'm a 17 year old from Assam building an AI startup while learning to code...")

niche = st.sidebar.selectbox("Niche", [
    "AI & Tech", "Fitness & Health", "Comedy",
    "Education", "Finance", "Fashion",
    "Gaming", "Food", "Travel", "Other"
])
if niche == "Other":
    niche = st.sidebar.text_input("Describe your niche")

content_style = st.sidebar.selectbox("Content Style", [
    "Educational", "Entertaining", "Inspirational",
    "Behind the scenes", "Storytelling", "Other"
])
if content_style == "Other":
    content_style = st.sidebar.text_input("Describe your style")

challenge = st.sidebar.selectbox("Biggest Challenge", [
    "Followers", "Engagement", "Ideas",
    "Consistency", "Standing out", "Other"
])
if challenge == "Other":
    challenge = st.sidebar.text_input("Describe your challenge")

target_audience = st.sidebar.selectbox("Target Audience", [
    "Students", "Professionals", "Entrepreneurs",
    "Parents", "Fitness lovers", "General", "Other"
])
if target_audience == "Other":
    target_audience = st.sidebar.text_input("Describe your audience")

analyze = st.sidebar.button("Analyze Profile")

st.sidebar.subheader("🎯 Post Scoring")
post_idea = st.sidebar.text_area("Enter Post Idea")
score_btn = st.sidebar.button("Score Idea")

# ---------------- LOGIC ----------------

if analyze:
    if followers == 0:
        st.error("Please enter your followers count!")
    else:
        engagement = round((likes / followers) * 100, 2)
        st.session_state.engagement = engagement
        with st.spinner("Analyzing viral potential..."):
            st.session_state.result = get_ai_suggestions(
                name, followers, engagement,
                niche, content_style,
                challenge, target_audience,
                about
            )

if "result" in st.session_state:
    engagement = st.session_state.engagement

    st.subheader(f"📊 {name}'s Analysis")
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
                st.warning("Needs improvement. Let's fix this!")
        elif followers < 10000:
            if engagement > 5:
                st.success("Excellent! Top tier 🔥")
            elif engagement > 2:
                st.info("Good! Above average 👍")
            else:
                st.warning("Needs improvement. Let's fix this!")
        else:
            if engagement > 3:
                st.success("Excellent! Top tier 🔥")
            elif engagement > 1:
                st.info("Good! Above average 👍")
            else:
                st.warning("Needs improvement. Let's fix this!")

    st.subheader("🔥 Viral Content Strategy")
    st.write(st.session_state.result)

    st.subheader("💬 Not happy with these ideas?")
    feedback = st.text_input("Tell us why and we'll generate better ones")
    regenerate = st.button("Regenerate Ideas")

    if regenerate and feedback:
        with st.spinner("Generating better ideas..."):
            st.session_state.result = get_ai_suggestions(
                name, followers, engagement,
                niche, content_style,
                challenge, target_audience,
                about, feedback
            )
        st.rerun()

if score_btn and post_idea:
    with st.spinner("Scoring idea..."):
        result = score_post(name, post_idea, followers)
    st.subheader("📊 Score Report")
    st.write(result)