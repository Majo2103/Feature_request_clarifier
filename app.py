import streamlit as st
import pandas as pd
from PIL import Image
from backend import questions_for_request, get_questions_list, definitions

# Inicializa estado
if 'stage' not in st.session_state:
    st.session_state.stage = 'input'
    st.session_state.responses = []
    st.session_state.question_index = 0
    st.session_state.questions_df = None
    st.session_state.questions_list = []

# Función de reinicio
def reset():
    st.session_state.stage = 'input'
    st.session_state.responses = []
    st.session_state.question_index = 0
    st.session_state.questions_df = None
    st.session_state.questions_list = []

# === General Style ===
st.markdown("""
    <style>
        body {
            background-color: #0C2340;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        textarea[disabled] {
            background-color: #0C2340;
            color: #0C2340;
        }
    </style>
""", unsafe_allow_html=True)

# === header ===
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("UTSA_Logo.svg.png", width=100)  # Usa tu imagen local aquí
with col_title:
    st.title("Feature Request Clarifier")

st.markdown("""
    <hr style="margin-top: 3rem; margin-bottom: 1rem;">
    <div style="text-align: center; color: #888;">
    This app helps you clarify your feature requests by asking targeted questions to remove ambiguities and incompleteness. If you want to know more about the methodology behind this app, <a href="https://arxiv.org/abs/2507.13555" target="_blank">read the paper</a>
    </div>
""", unsafe_allow_html=True)
st.divider()

# === main screen ===
if st.session_state.stage == 'input':
    st.markdown("Write your feature request below❗❗❗")
    original_request = st.text_area("", height=150)
    original_title = st.text_input("Request Title")


    col_go, col_restart = st.columns([1, 5])
    with col_go:
        if st.button("GO🚀"):
            if original_request.strip():
                df = questions_for_request(original_request, original_title)
                if not df.empty:
                    st.session_state.questions_df = df.copy()
                    st.session_state.questions_list = get_questions_list(df)
                    st.session_state.stage = 'questions'
                else:
                    st.warning("No ambiguous segments found.")
            else:
                st.warning("Please enter a feature request.")
    with col_restart:
        if st.button("Restart ↺"):
            reset()

# === questions screen ===
elif st.session_state.stage == 'questions':
    df = st.session_state.questions_df
    q_list = st.session_state.questions_list
    idx = st.session_state.question_index
    total = len(q_list)
    remaining = total - idx

    st.subheader("Your original request:")
    st.text_area("", df.loc[0, "original_request"], disabled=True, height=120)

    if idx < total:
        row = q_list[idx]
        question = row["question"]
        segment = row["segment"]
        defect = row["defect_type"]
        row_index = row["row_index"]

        st.markdown("### ❓ Clarifying question")
        st.markdown(f"**{question}**")
        user_answer = st.text_input("Your answer", key=f"answer_{idx}")

        col_enter, col_why, col_restart = st.columns([2, 1, 1])
        with col_enter:
            if st.button("Enter"):
                if user_answer.strip():
                    st.session_state.questions_df.at[row_index, "user_response"] = user_answer
                    st.session_state.question_index += 1
                    st.rerun()
                else:
                    st.warning("Please provide an answer.")

        with col_why:
            if st.button("Why?"):
                definition = definitions.get(defect.lower(), "Definition not available.")
                with st.expander("🔍 Explanation"):
                    st.markdown(f"- **Segment**: `{segment}`")
                    st.markdown(f"- **Defect Type**: `{defect}`")
                    st.markdown(f"- **Definition**: {definition}")

        with col_restart:
            if st.button("Restart"):
                reset()

        st.markdown(f"📌 **{remaining} question(s) remaining**")

    else:
        st.success("✅ Your request has been refined. Thank you!")
        st.dataframe(st.session_state.questions_df[["segment", "defect_type", "question", "user_response"]])
        if st.button("Restart"):
            reset()

# === Footer bonito ===
st.markdown("""
    <hr style="margin-top: 3rem; margin-bottom: 1rem;">
    <div style="text-align: center; color: #888;">
        Made with 💛 by Majo Velázquez · <a href="https://github.com/Majo2103" target="_blank">GitHub</a> · <a href="https://www.linkedin.com/in/mar%C3%ADa-jos%C3%A9-vel%C3%A1zquez-ba%C3%B1ares-2bb54323b/" target="_blank">LinkedIn</a>
    </div>
""", unsafe_allow_html=True)