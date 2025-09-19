import streamlit as st
import requests
import pandas as pd

# Base URL for your API
API_URL_BASE = "http://127.0.0.1:8000"

# --- Page Configuration ---
st.set_page_config(
    page_title="Cyber Threat Intel Platform",
    page_icon="🤖",
    layout="wide"
)

# --- App Title ---
st.title("🤖 AI-Powered Cyber Threat Intelligence Briefing")
st.write("This dashboard displays the top prioritized cyber threats. Click on a threat to view the AI-generated analysis.")

# --- Fetch and Display Data ---
try:
    # Make a request to the backend API's prioritized endpoint
    response = requests.get(f"{API_URL_BASE}/threats/prioritized/")
    response.raise_for_status()
    threat_data = response.json()

    if not threat_data:
        st.info("No threat data found. Please run the `ingest.py` script to populate the database.")
    else:
        # Loop through each threat and display it as an expandable card
        for threat in threat_data:
            with st.expander(f"**Score: {threat['priority_score']}** | {threat['title']}"):
                
                st.subheader("AI Analyst Summary")
                st.info(threat['ai_summary'])

                # Create two columns for better layout
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Key Entities")
                    st.markdown(f"*{threat['ai_entities']}*")

                with col2:
                    st.subheader("Source & Type")
                    st.markdown(f"**Source:** {threat['source']}\n\n**Type:** {threat['type']}")

                st.subheader("Actionable Mitigation Steps")
                st.success(threat['ai_mitigation'])

                # --- THIS IS THE NEW CISO BRIEFING GENERATOR BUTTON ---
                st.divider()
                if st.button("Generate CISO Briefing", key=f"ciso_{threat['id']}"):
                    with st.spinner("AI Analyst is generating the CISO briefing..."):
                        try:
                            briefing_response = requests.post(f"{API_URL_BASE}/threats/{threat['id']}/ciso_briefing/")
                            briefing_response.raise_for_status()
                            briefing_data = briefing_response.json()
                            
                            st.subheader("Executive (CISO) Briefing")
                            st.markdown(briefing_data['briefing'])
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to generate briefing: {e}")

except requests.exceptions.RequestException:
    st.error("Could not connect to the backend API. Please make sure the FastAPI server is running.")

