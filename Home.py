import streamlit as st

st.set_page_config(
    page_title="Cyber Threat Intel Platform",
    page_icon="🤖",
    layout="wide"
)

st.title("Welcome to the AI-Powered Cyber Threat Intelligence Platform")
st.sidebar.success("Select a feature above.")

st.markdown(
    """
    This platform provides real-time, AI-driven analysis of global cyber threats.
    
    ### Key Features:
    - **Threat Briefing:** View a prioritized list of the latest threats with detailed AI analysis.
    - **Practical Assessments:** Test your knowledge with AI-generated quizzes based on real-world threats.

    Select a feature from the sidebar to get started.
    """
)
