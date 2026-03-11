import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"
TOTAL_QUESTIONS = 10


def api_post(url, data=None):
    r = requests.post(url, json=data)
    if r.status_code != 200:
        st.error(r.json().get("detail", "API Error"))
        return None
    return r.json()


def api_get(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


st.title("Adaptive Diagnostic Engine")

# ---------- SESSION INITIALIZATION ----------

if "session_id" not in st.session_state:

    session = api_post(f"{API_URL}/start_session")

    st.session_state.session_id = session["session_id"]
    st.session_state.q_index = 0
    st.session_state.question = None
    st.session_state.feedback = None
    st.session_state.study_plan = None
    st.session_state.difficulties = []


# ---------- SHOW SESSION ID ----------

st.sidebar.header("API Session")

st.sidebar.code(st.session_state.session_id)

st.sidebar.caption("Use this session ID with Postman or curl")

st.sidebar.markdown("Example API calls")

st.sidebar.code(
f"""GET /next_question/{st.session_state.session_id}
POST /submit_answer/{st.session_state.session_id}
GET /study_plan/{st.session_state.session_id}
""",
language="bash"
)


# ---------- PROGRESS BAR ----------

answered = st.session_state.q_index
if st.session_state.feedback:
    answered += 1

st.progress(min(answered / TOTAL_QUESTIONS, 1.0))


# ---------- REPORT VIEW ----------

if st.session_state.study_plan:

    data = st.session_state.study_plan

    st.header("Diagnostic Report")

    st.metric("Final Ability Estimate", f"{data['final_ability']:.2f}")
    st.metric("Performance Score", f"{data['performance_score']:.2f}")

    st.subheader("Ability Progression")

    ability_history = data["ability_history"]

    ability_df = pd.DataFrame({
        "Question": list(range(1, len(ability_history) + 1)),
        "Ability": ability_history
    }).set_index("Question")

    st.line_chart(ability_df)

    if st.session_state.difficulties:

        chart = pd.DataFrame({
            "Question": list(range(1, len(st.session_state.difficulties) + 1)),
            "Ability": ability_history[1:],
            "Difficulty": st.session_state.difficulties
        }).set_index("Question")

        st.subheader("Question Difficulty vs Ability")

        st.line_chart(chart)

    st.subheader("Topic Errors")
    st.write(data["topic_errors"])

    st.subheader("Personalized Study Plan")
    st.write(data["study_plan"])

    if st.button("Restart Test"):
        st.session_state.clear()
        st.rerun()


# ---------- TEST FLOW ----------

else:

    if st.session_state.question is None and st.session_state.q_index < TOTAL_QUESTIONS:

        q = api_get(f"{API_URL}/next_question/{st.session_state.session_id}")

        if q:
            st.session_state.question = q
            st.session_state.difficulties.append(q["difficulty"])

    q = st.session_state.question

    if q is None:
        st.stop()

    st.subheader(f"Question {st.session_state.q_index + 1}/{TOTAL_QUESTIONS}")

    st.write(q["question_text"])
    st.caption(f"Topic: {q['topic']}")
    st.caption(f"Difficulty: {q['difficulty']:.2f}")

    options = list(q["options"].keys())

    answer = st.radio(
        "Choose an option",
        options,
        format_func=lambda x: f"{x}: {q['options'][x]}",
    )

    if st.button("Submit Answer") and st.session_state.feedback is None:

        result = api_post(
            f"{API_URL}/submit_answer/{st.session_state.session_id}",
            {"answer": answer},
        )

        if result:
            st.session_state.feedback = result
            st.rerun()

    if st.session_state.feedback:

        if st.session_state.feedback["correct"]:
            st.success("Correct")
        else:
            st.error("Incorrect")

        st.info(f"Estimated Ability: {st.session_state.feedback['new_ability']:.2f}")

        if st.session_state.q_index == TOTAL_QUESTIONS - 1:

            if st.button("Finish Test"):

                plan = api_get(
                    f"{API_URL}/study_plan/{st.session_state.session_id}"
                )

                if plan:
                    st.session_state.study_plan = plan
                    st.rerun()

        else:

            if st.button("Next Question"):

                st.session_state.q_index += 1
                st.session_state.question = None
                st.session_state.feedback = None

                st.rerun()