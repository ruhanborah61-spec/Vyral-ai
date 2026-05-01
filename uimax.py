import streamlit as st
import random

st.set_page_config(page_title="CreatorAI Dashboard", layout="wide")

# Sidebar
st.sidebar.title("CreatorAI")
menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Content Ideas",
    "Post Schedule",
    "Audience Insights",
    "Style Profile",
    "Settings"
])

# User Input
st.sidebar.markdown("---")
st.sidebar.subheader("Your Stats")
name = st.sidebar.text_input("Name", "Ruhan")
followers = st.sidebar.number_input("Followers", min_value=0, value=1000)
likes = st.sidebar.number_input("Average Likes", min_value=0, value=150)

# Metrics calculation
engagement_rate = (likes / followers * 100) if followers > 0 else 0
best_time = random.choice(["6 PM", "8 PM", "9 PM", "7 AM"])

# Dashboard UI
if menu == "Dashboard":
    st.title(f"Welcome, {name} 👋")
    st.caption("Your AI Growth Manager")

    # Metric Cards
    col1, col2, col3 = st.columns(3)

    col1.metric("Followers", followers)
    col2.metric("Engagement Rate", f"{engagement_rate:.2f}%")
    col3.metric("Best Time to Post", best_time)

    st.markdown("---")

    # AI Content Ideas
    st.subheader("🔥 AI Content Ideas For You")

    ideas = [
        "Day in the life of a 17 y/o building an AI startup in Assam",
        "How I built my own AI app using only a laptop",
        "Things I wish I knew before starting coding at 16"
    ]

    for idea in ideas:
        st.info(idea)

    st.markdown("---")

    # Post Score Predictor
    st.subheader("📊 Post Score Predictor")

    hook = st.slider("Hook Strength", 0, 100, 70)
    share = st.slider("Shareability", 0, 100, 65)
    trend = st.slider("Trend Match", 0, 100, 60)
    audience = st.slider("Audience Fit", 0, 100, 75)

    st.write("### Score Breakdown")
    st.progress(hook)
    st.write("Hook Strength")

    st.progress(share)
    st.write("Shareability")

    st.progress(trend)
    st.write("Trend Match")

    st.progress(audience)
    st.write("Audience Fit")

# Other Pages
elif menu == "Content Ideas":
    st.title("Content Ideas")
    st.write("AI-generated ideas will appear here.")

elif menu == "Post Schedule":
    st.title("Post Schedule")
    st.write("Plan your posts here.")

elif menu == "Audience Insights":
    st.title("Audience Insights")
    st.write("Understand your audience.")

elif menu == "Style Profile":
    st.title("Style Profile")
    st.write("Define your content style.")

elif menu == "Settings":
    st.title("Settings")
    st.write("Manage your preferences.")
