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

# ---------------- AI PROMPT ENGINE ----------------

def get_ai_suggestions(name, followers, engagement, niche, content_style, challenge, target_audience, about, feedback=""):
    feedback_text = f"\nUSER FEEDBACK:\n{feedback}\nGenerate a completely different idea addressing this concern.\n" if feedback else ""

    prompt = f"""
You are a viral content drill sergeant.
You don't give options. You give orders.
Your job is to tell {name} exactly what to post — one video, one decision, one action.

USER DATA:
Name: {name}
About: {about}
Niche: {niche}
Content Style: {content_style}
Challenge: {challenge}
Target Audience: {target_audience}
Followers: {followers}
Engagement: {engagement}%

OUTPUT FORMAT (STRICT — NO CHANGES):

{name}'s problem: [one brutal diagnosis in simple language]

YOUR BEST POST (POST THIS TOMORROW):
Platform: [exact platform]
Best time: [exact time]

Hook (0-2 sec):
"[exact words to say]"
[exact visual — phone recordable, no equipment needed]

Execution:
0-3 sec: [exact action]
3-10 sec: [exact action]
10-18 sec: [exact action]
18-20 sec: [exact CTA words]

Why this will work: [one line]

What to avoid: [2-3 things killing their reach right now]

One rule to follow for every video: [one simple rule]

Come back after posting — I'll fix your next video.

STRICT RULES:
- ONE idea only. Not three.
- No long explanations
- Every step must be doable with just a phone
- No technical terms without simple explanation in brackets
- Maximum 3 execution steps only
- NO acting scenes, NO fake emotions, NO props
- Show RESULT first, explain later
- Hook must use ONE of these emotions:
  * "you're behind" (FOMO)
  * "you're wasting time" (urgency)  
  * "no one tells you this" (secret)
  * "I stopped doing X and this happened" (surprise)
- Never state facts. Always trigger emotion.
- Make viewer feel: "I'm missing out if I don't try this"
- Avoid hooks that sound like complaints or rants
- Talk directly to {name} throughout
- Be decisive. Be a drill sergeant. Not a consultant.

{feedback_text}
"""
    return call_groq(prompt)

# ---------------- SCORING ENGINE ----------------

def score_post(name, post_idea, followers):
    prompt = f"""
You are a strict viral content analyst.
Be direct and decisive. No fluff.

Creator: {name}
Followers: {followers}

Post idea:
{post_idea}

OUTPUT FORMAT (STRICT):

Hook Score: /100
Shareability: /100
Trend Match: /100
Audience Fit: /100

Biggest weakness: [one line]
Fix it: [one specific action]
Verdict: [Post it / Don't post it / Fix this first]
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
post_idea = st.sidebar.text_area("Describe your post idea")
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

    st.subheader("🔥 Your Viral Content Strategy")
    st.write(st.session_state.result)

    st.subheader("💬 Not happy with this idea?")
    feedback = st.text_input("Tell us why and we'll generate a better one")
    regenerate = st.button("Regenerate Idea")

    if regenerate and feedback:
        with st.spinner("Generating better idea..."):
            st.session_state.result = get_ai_suggestions(
                name, followers, engagement,
                niche, content_style,
                challenge, target_audience,
                about, feedback
            )
        st.rerun()