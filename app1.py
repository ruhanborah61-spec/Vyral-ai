import streamlit as st
import google.generativeai as genai

# 🔑 API KEY
genai.configure(api_key="AIzaSyB1yBq3QYy4IA1hhZx1bYcBX_pchZ7eluU")

model = genai.GenerativeModel("gemini-pro")

# ---------- UI ----------
st.set_page_config(page_title="CreatorAI", layout="wide")

st.title("🚀 CreatorAI - AI Growth Manager for Creators")

# ---------- Sidebar ----------
st.sidebar.header("📊 Creator Profile")

name = st.sidebar.text_input("Your Name")
followers = st.sidebar.number_input("Followers", min_value=0)
likes = st.sidebar.number_input("Average Likes per post", min_value=0)

st.sidebar.markdown("---")
st.sidebar.write("💡 CreatorAI helps you grow faster with AI insights")

# ---------- Main Dashboard ----------
col1, col2, col3 = st.columns(3)

engagement = 0
if followers > 0:
    engagement = round((likes / followers) * 100, 2)

col1.metric("Followers", followers)
col2.metric("Avg Likes", likes)
col3.metric("Engagement Rate", f"{engagement}%")

st.markdown("---")

# ---------- AI Section ----------
st.subheader("🤖 AI Content Assistant")
user_prompt = st.text_area("Ask CreatorAI (content ideas, captions, growth tips)")
if st.button("🧪 Test Gemini"):
    response = model.generate_content("Say hello in one line")
    st.write(response.text)
if st.button("Generate"):
    if user_prompt.strip() != "":
        with st.spinner("Thinking..."):
            response = model.generate_content(
                f"You are CreatorAI, a growth assistant for social media creators.\nUser: {user_prompt}"
            )
        st.success(response.text)
    else:
        st.warning("Please enter a prompt")

# ---------- Content Ideas ----------
st.subheader("💡 Quick Content Ideas")

if st.button("Generate 5 Viral Ideas"):
    with st.spinner("Generating ideas..."):
        response = model.generate_content(
            "Give 5 viral social media content ideas for a beginner creator."
        )
    st.write(response.text)
    