import streamlit as st
import requests

# Base URL for your API
API_URL_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Practical Assessments",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 AI-Powered Threat Simulation Quiz")
st.write("Test your knowledge on real-world threats with an AI-generated quiz.")

try:
    # Fetch all threats to populate the dropdown
    threats_response = requests.get(f"{API_URL_BASE}/threats/")
    threats_response.raise_for_status()
    threats_data = threats_response.json()
    
    if not threats_data:
        st.warning("No threats found in the database. Please run `ingest.py` first.")
    else:
        # Create a dictionary mapping threat titles to their IDs for the selectbox
        threat_titles = {threat['title']: threat['id'] for threat in threats_data}
        selected_title = st.selectbox("Select a Threat to be Quizzed On:", options=threat_titles.keys())

        if st.button("Start Threat Simulation Quiz"):
            threat_id = threat_titles[selected_title]
            with st.spinner("AI Instructor is generating your quiz..."):
                try:
                    quiz_response = requests.post(f"{API_URL_BASE}/assessments/{threat_id}/generate/")
                    quiz_response.raise_for_status()
                    # Store quiz data in session state to preserve it across reruns
                    st.session_state.quiz_questions = quiz_response.json()
                    st.session_state.user_answers = [None] * len(st.session_state.quiz_questions)
                    st.session_state.quiz_submitted = False
                    st.session_state.current_quiz_title = selected_title
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to generate quiz: {e}")

        # Display the quiz if it has been generated and not yet submitted
        if 'quiz_questions' in st.session_state and not st.session_state.quiz_submitted:
            st.divider()
            st.subheader(f"Quiz for: *{st.session_state.current_quiz_title}*")

            # Create a form to hold the questions and the submit button
            with st.form(key='quiz_form'):
                for i, q in enumerate(st.session_state.quiz_questions):
                    st.session_state.user_answers[i] = st.radio(q['question'], q['options'], key=f"q_{i}")
                
                submitted = st.form_submit_button("Submit Answers")
                if submitted:
                    st.session_state.quiz_submitted = True
                    st.experimental_rerun()

        # Display results after submission
        if 'quiz_submitted' in st.session_state and st.session_state.quiz_submitted:
            st.divider()
            st.subheader("Quiz Results")
            score = 0
            for i, q in enumerate(st.session_state.quiz_questions):
                user_answer = st.session_state.user_answers[i]
                correct_answer = q['answer']
                
                if user_answer == correct_answer:
                    score += 1
                    st.success(f"**Question {i+1}: Correct!**")
                else:
                    st.error(f"**Question {i+1}: Incorrect.**")
                    st.write(f"Correct answer: **{correct_answer}**")
                
                st.info(f"**Explanation:** {q['explanation']}")
                st.divider()

            st.balloons()
            st.success(f"**Your final score: {score} out of {len(st.session_state.quiz_questions)}**")
            
            if st.button("Take Another Quiz"):
                # Clear session state to reset the page
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()

except requests.exceptions.RequestException:
    st.error("Could not connect to the backend API. Please make sure the FastAPI server is running.")

