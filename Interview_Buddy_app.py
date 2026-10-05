import streamlit as st
import ollama
import re
import tempfile
from pathlib import Path

from streamlit_mic_recorder import mic_recorder
from faster_whisper import WhisperModel


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="InterviewBuddy AI",
    page_icon="🤖",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at 10% 0%, rgba(99,102,241,.18), transparent 30%), radial-gradient(circle at 90% 10%, rgba(59,130,246,.14), transparent 28%), linear-gradient(135deg,#070b17 0%,#0d1324 48%,#111827 100%); }
.block-container { max-width:1180px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0a1020 0%,#11182b 100%); border-right:1px solid rgba(148,163,184,.14); }
.hero { padding:34px 38px; border-radius:26px; border:1px solid rgba(129,140,248,.25); background:linear-gradient(135deg,rgba(79,70,229,.22),rgba(37,99,235,.10)),rgba(15,23,42,.72); box-shadow:0 20px 55px rgba(0,0,0,.25); margin-bottom:26px; }
.hero-badge { display:inline-block; padding:7px 13px; border-radius:999px; background:rgba(129,140,248,.14); border:1px solid rgba(129,140,248,.25); color:#c7d2fe; font-size:12px; font-weight:800; letter-spacing:1px; margin-bottom:12px; }
.main-title { font-size:clamp(38px,5vw,58px); line-height:1.05; font-weight:900; letter-spacing:-1.5px; margin:0; color:#f8fafc; }
.subtitle { font-size:18px; color:#aab6cc; margin-top:12px; }
.section-label { font-size:13px; text-transform:uppercase; letter-spacing:1.5px; font-weight:800; color:#a5b4fc; margin-bottom:4px; }
.section-title { font-size:30px; font-weight:850; color:#f8fafc; margin-bottom:8px; }
.question-card,.voice-card,.score-card { border-radius:20px; border:1px solid rgba(148,163,184,.16); background:rgba(15,23,42,.72); box-shadow:0 15px 40px rgba(0,0,0,.18); }
.question-card { padding:28px; margin:12px 0 24px; background:linear-gradient(135deg,rgba(79,70,229,.17),rgba(15,23,42,.82)); border-color:rgba(129,140,248,.25); }
.question-number { color:#a5b4fc; font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:1.4px; margin-bottom:10px; }
.question-text { color:#f8fafc; font-size:24px; line-height:1.45; font-weight:700; }
.voice-card { padding:20px; margin:8px 0 18px; background:rgba(30,41,59,.72); }
.score-card { text-align:center; padding:28px; margin:16px 0 22px; background:radial-gradient(circle at 50% 0%,rgba(34,197,94,.12),transparent 55%),rgba(15,23,42,.82); }
.score-label { color:#94a3b8; font-size:13px; text-transform:uppercase; letter-spacing:1.5px; font-weight:800; }
.score-number { font-size:58px; line-height:1; font-weight:900; color:#86efac; margin:8px 0; }
.score-status { color:#cbd5e1; font-size:14px; }
[data-testid="stMetric"] { background:rgba(15,23,42,.68); border:1px solid rgba(148,163,184,.14); padding:16px; border-radius:16px; }
.stButton > button { border-radius:12px; min-height:46px; font-weight:750; border:1px solid rgba(129,140,248,.22); background:linear-gradient(135deg,#4f46e5,#2563eb); color:white; box-shadow:0 8px 22px rgba(37,99,235,.18); }
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"] > div { border-radius:12px !important; }
.stProgress > div > div { border-radius:999px; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:10px 10px 0 0; padding:10px 16px; }
div[data-testid="stAlert"] { border-radius:14px; }
.footer { text-align:center; color:#64748b; font-size:12px; padding:18px 0 4px; }

/* SIDEBAR ONLY — does not change main page sizing/alignment */
[data-testid="stSidebar"] > div:first-child { padding-top:1.5rem; }
.sidebar-brand { padding:18px 16px; border-radius:18px; background:linear-gradient(145deg,rgba(79,70,229,.20),rgba(37,99,235,.08)); border:1px solid rgba(129,140,248,.22); margin-bottom:18px; }
.sidebar-brand-title { font-size:21px; font-weight:850; color:#f8fafc; margin:0 0 4px 0; }
.sidebar-brand-subtitle { font-size:12px; line-height:1.5; color:#94a3b8; margin:0; }
.sidebar-section-label { font-size:11px; text-transform:uppercase; letter-spacing:1.4px; font-weight:800; color:#a5b4fc; margin:4px 0 10px 2px; }
.sidebar-feature { display:flex; align-items:center; gap:10px; padding:9px 10px; margin:5px 0; border-radius:11px; background:rgba(30,41,59,.48); border:1px solid rgba(148,163,184,.09); color:#dbe4f0; font-size:13px; line-height:1.25; }
.sidebar-feature:hover { background:rgba(79,70,229,.12); border-color:rgba(129,140,248,.18); }
.sidebar-feature-icon { width:25px; min-width:25px; height:25px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:rgba(99,102,241,.14); font-size:14px; }
.sidebar-tech { padding:13px 14px; border-radius:14px; background:rgba(15,23,42,.55); border:1px solid rgba(148,163,184,.10); }
.sidebar-tech-title { font-size:11px; text-transform:uppercase; letter-spacing:1.2px; font-weight:800; color:#64748b; margin-bottom:7px; }
.sidebar-tech-line { font-size:12px; color:#aab6cc; line-height:1.7; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "started": False,
    "question": "",
    "answer": "",
    "feedback": "",
    "question_number": 0,
    "scores": [],
    "interview_finished": False,
    "category": "Mixed"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# GEMMA FUNCTION
# =========================================================

def ask_gemma(prompt):

    response = ollama.chat(
        model="gemma3:latest",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# =========================================================
# WHISPER MODEL
# =========================================================

@st.cache_resource
def load_whisper_model():

    model = WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8"
    )

    return model


# =========================================================
# AUDIO TRANSCRIPTION
# =========================================================

def transcribe_audio(audio_bytes):

    model = load_whisper_model()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(audio_bytes)
        audio_path = temp_audio.name

    try:

        segments, info = model.transcribe(
            audio_path,
            beam_size=5
        )

        transcript = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        return transcript

    finally:

        try:
            Path(audio_path).unlink(missing_ok=True)

        except Exception:
            pass


# =========================================================
# GENERATE QUESTION
# =========================================================

def generate_question(
    job_role,
    experience,
    category,
    question_number
):

    prompt = f"""

You are a professional interview coach.

Create ONE realistic interview question.

Job Role: {job_role}

Experience Level: {experience}

Interview Category: {category}

Question Number: {question_number}

If category is Mixed, choose a suitable
technical, practical, situational, or HR question.

For beginners use clear language.

Return ONLY the question.

Do not give the answer.

"""

    return ask_gemma(prompt)


# =========================================================
# EVALUATE ANSWER
# =========================================================

def evaluate_answer(
    question,
    answer,
    job_role
):

    prompt = f"""

You are a professional and supportive interview coach.

Job Role: {job_role}

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the candidate fairly.

Give EXACTLY these sections:

1. SCORE: X/10
2. Strengths
3. Areas to Improve
4. Better Answer
5. Follow-up Question
6. Communication Tip

Keep feedback clear,
constructive and beginner-friendly.

"""

    return ask_gemma(prompt)


# =========================================================
# EXTRACT SCORE
# =========================================================

def extract_score(feedback):

    match = re.search(
        r"SCORE\s*:\s*(\d+(?:\.\d+)?)\s*/\s*10",
        feedback,
        re.IGNORECASE
    )

    if match:

        return max(
            0.0,
            min(
                float(match.group(1)),
                10.0
            )
        )

    return None


# =========================================================
# RESET INTERVIEW
# =========================================================

def reset_interview():

    st.session_state.started = False

    st.session_state.question = ""

    st.session_state.answer = ""

    st.session_state.feedback = ""

    st.session_state.question_number = 0

    st.session_state.scores = []

    st.session_state.interview_finished = False


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '''
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">🤖 InterviewBuddy AI</div>
            <p class="sidebar-brand-subtitle">
                Your private local AI interview coach
            </p>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section-label">What you can practice</div>',
        unsafe_allow_html=True
    )

    features = [
        ("🎯", "Mock interview"),
        ("🎙️", "Voice interview mode"),
        ("📝", "Local speech-to-text"),
        ("🤖", "Gemma 3 feedback"),
        ("📊", "Question scoring"),
        ("💡", "Better-answer suggestions"),
        ("🔄", "Follow-up questions"),
        ("🏆", "Final performance report")
    ]

    for icon, feature in features:
        st.markdown(
            f'''
            <div class="sidebar-feature">
                <span class="sidebar-feature-icon">{icon}</span>
                <span>{feature}</span>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        '''
        <div class="sidebar-tech">
            <div class="sidebar-tech-title">⚡ Powered locally</div>
            <div class="sidebar-tech-line">
                🔒 Your interview stays on your machine<br>
                🧠 Ollama + Gemma 3<br>
                🎙️ Faster-Whisper for voice<br>
                🐍 Python + Streamlit
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


# =========================================================
# MAIN TITLE
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">✨ LOCAL AI INTERVIEW COACH</div>
        <div class="main-title">🤖 InterviewBuddy AI</div>
        <div class="subtitle">Practice smarter. Speak naturally. Get instant AI feedback.</div>
    </div>
    """, unsafe_allow_html=True
)


# =========================================================
# START INTERVIEW SCREEN
# =========================================================

if not st.session_state.started:

    st.markdown('<div class="section-label">INTERVIEW SETUP</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Start Your Mock Interview</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)


    # -----------------------------------------------------
    # LEFT COLUMN
    # -----------------------------------------------------

    with col1:

        job_role = st.text_input(
            "💼 Job Role",
            placeholder="Example: Data Analyst"
        )

        experience = st.selectbox(
            "🎓 Experience Level",
            [
                "Beginner",
                "Intermediate",
                "Experienced"
            ]
        )


    # -----------------------------------------------------
    # RIGHT COLUMN
    # -----------------------------------------------------

    with col2:

        category = st.selectbox(
            "📚 Interview Category",
            [
                "Mixed",
                "Technical",
                "HR",
                "Situational",
                "Practical"
            ]
        )

        total_questions = st.selectbox(
            "📝 Number of Questions",
            [
                2,
                4,
                6,
                8,
                10
            ],
            index=1
        )


    st.info(
        "Answer each question naturally. "
        "You can type your answer or use "
        "the new Voice Interview Mode. "
        "Gemma 3 will give a score, strengths, "
        "improvements and a follow-up question."
    )


    # -----------------------------------------------------
    # START BUTTON
    # -----------------------------------------------------

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):

        if not job_role.strip():

            st.warning(
                "⚠️ Please enter a job role first!"
            )

        else:

            st.session_state.started = True

            st.session_state.job_role = (
                job_role.strip()
            )

            st.session_state.experience = (
                experience
            )

            st.session_state.category = (
                category
            )

            st.session_state.total_questions = (
                total_questions
            )

            st.session_state.question_number = 1

            st.session_state.scores = []

            st.session_state.feedback = ""

            st.session_state.answer = ""

            st.session_state.interview_finished = False


            with st.spinner(
                "🤖 Gemma 3 is preparing your first question..."
            ):

                st.session_state.question = (
                    generate_question(
                        st.session_state.job_role,
                        st.session_state.experience,
                        st.session_state.category,
                        1
                    )
                )

            st.rerun()


# =========================================================
# FINAL REPORT
# =========================================================

elif st.session_state.interview_finished:

    st.markdown('<div class="section-label">FINAL REPORT</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏆 Interview Complete!</div>', unsafe_allow_html=True)

    scores = st.session_state.scores


    if scores:

        average = sum(scores) / len(scores)


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Overall Score",
                f"{average:.1f}/10"
            )


        with col2:

            st.metric(
                "Questions Completed",
                len(scores)
            )


        with col3:

            st.metric(
                "Highest Score",
                f"{max(scores):.1f}/10"
            )


        st.progress(
            min(
                average / 10,
                1.0
            )
        )


        # -------------------------------------------------
        # PERFORMANCE MESSAGE
        # -------------------------------------------------

        if average >= 8:

            st.success(
                "🌟 Excellent performance! "
                "Keep practicing."
            )

        elif average >= 6:

            st.info(
                "👍 Good performance! "
                "Work on the improvement points."
            )

        else:

            st.warning(
                "💪 Keep practicing answer structure, "
                "examples and clarity."
            )


        # -------------------------------------------------
        # QUESTION PERFORMANCE
        # -------------------------------------------------

        st.subheader(
            "📊 Question-wise Performance"
        )


        for i, score in enumerate(
            scores,
            start=1
        ):

            st.write(
                f"**Question {i}: "
                f"{score:.1f}/10**"
            )

            st.progress(
                min(
                    score / 10,
                    1.0
                )
            )


        # -------------------------------------------------
        # FINAL TIPS
        # -------------------------------------------------

        st.subheader(
            "💡 Final Preparation Tips"
        )


        tips = [

            "Keep answers clear and structured.",

            "Use real examples whenever possible.",

            "Avoid extremely short answers.",

            "Explain your thinking step-by-step "
            "for technical questions.",

            "Practice speaking confidently "
            "and naturally.",

            "Review questions where your score "
            "was lower."

        ]


        for tip in tips:

            st.write(
                f"• {tip}"
            )


    else:

        st.warning(
            "No scored answers were recorded."
        )


    st.divider()


    if st.button(
        "🔄 Start New Interview",
        use_container_width=True
    ):

        reset_interview()

        st.rerun()


# =========================================================
# ACTIVE INTERVIEW
# =========================================================

else:

    current = (
        st.session_state.question_number
    )

    total = (
        st.session_state.total_questions
    )


    # -----------------------------------------------------
    # QUESTION HEADER
    # -----------------------------------------------------

    col1, col2 = st.columns(
        [3, 1]
    )


    with col1:

        st.subheader(
            f"🎤 Question {current} "
            f"of {total}"
        )


    with col2:

        st.metric(
            "Answered",
            len(st.session_state.scores)
        )


    st.progress(
        (current - 1) / total
    )


    st.caption(
        f"💼 {st.session_state.job_role}  •  "
        f"🎓 {st.session_state.experience}  •  "
        f"📚 {st.session_state.category}"
    )


    st.divider()


    # -----------------------------------------------------
    # QUESTION
    # -----------------------------------------------------

    st.markdown('<div class="section-label">INTERVIEWER</div>', unsafe_allow_html=True)
    st.markdown(
        f'''
        <div class="question-card">
            <div class="question-number">📝 Your Interview Question</div>
            <div class="question-text">{st.session_state.question}</div>
        </div>
        ''', unsafe_allow_html=True
    )


    # =====================================================
    # ANSWER AREA
    # =====================================================

    st.markdown('<div class="section-label">YOUR RESPONSE</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎤 How would you answer?</div>', unsafe_allow_html=True)


    text_tab, voice_tab = st.tabs(
        [
            "⌨️ Type Answer",
            "🎙️ Voice Answer"
        ]
    )


    # =====================================================
    # TEXT ANSWER
    # =====================================================

    with text_tab:

        answer = st.text_area(
            "Write your answer here:",
            value=st.session_state.answer,
            placeholder=(
                "Type your answer as if you "
                "are speaking to a real interviewer..."
            ),
            height=180,
            key=f"answer_box_{current}"
        )


        if st.button(
            "💡 Submit Typed Answer",
            use_container_width=True
        ):

            if not answer.strip():

                st.warning(
                    "⚠️ Please write your answer first."
                )

            else:

                st.session_state.answer = answer


                with st.spinner(
                    "🤖 Gemma 3 is analyzing your answer..."
                ):

                    feedback = evaluate_answer(
                        st.session_state.question,
                        answer,
                        st.session_state.job_role
                    )


                st.session_state.feedback = feedback


                score = extract_score(
                    feedback
                )


                if score is not None:

                    st.session_state.scores.append(
                        score
                    )


                st.rerun()


    # =====================================================
    # VOICE ANSWER
    # =====================================================

    with voice_tab:

        st.markdown(
            '''
            <div class="voice-card">
            🎙️ <strong>Voice Interview Mode</strong><br>
            Click the microphone, speak your answer
            naturally, then stop recording.
            Your speech will be converted into text
            locally using Faster-Whisper.
            </div>
            ''',
            unsafe_allow_html=True
        )


        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            format="wav",
            key=f"voice_recorder_{current}"
        )


        # -------------------------------------------------
        # PROCESS AUDIO
        # -------------------------------------------------

        if audio is not None:

            if isinstance(audio, dict):

                audio_bytes = audio.get(
                    "bytes"
                )

            else:

                audio_bytes = None


            if audio_bytes:

                with st.spinner(
                    "📝 Converting your voice to text..."
                ):

                    try:

                        transcript = (
                            transcribe_audio(
                                audio_bytes
                            )
                        )


                        if transcript:

                            st.session_state.answer = (
                                transcript
                            )

                            st.success(
                                "✅ Voice converted to text!"
                            )

                        else:

                            st.warning(
                                "⚠️ I couldn't detect clear "
                                "speech. Please try again."
                            )


                    except Exception as e:

                        st.error(
                            f"❌ Voice transcription failed: {e}"
                        )


        # -------------------------------------------------
        # SHOW TRANSCRIPT
        # -------------------------------------------------

        if st.session_state.answer:

            st.text_area(
                "📝 Transcribed Answer "
                "(you can edit it):",

                value=st.session_state.answer,

                height=180,

                key=f"voice_transcript_{current}"
            )


        # -------------------------------------------------
        # SUBMIT VOICE ANSWER
        # -------------------------------------------------

        if st.button(
            "🤖 Submit Voice Answer",
            use_container_width=True
        ):

            voice_answer = st.session_state.get(
                f"voice_transcript_{current}",
                st.session_state.answer
            )


            if not voice_answer.strip():

                st.warning(
                    "⚠️ Please record an answer first."
                )


            else:

                st.session_state.answer = (
                    voice_answer
                )


                with st.spinner(
                    "🤖 Gemma 3 is analyzing your answer..."
                ):

                    feedback = evaluate_answer(
                        st.session_state.question,
                        voice_answer,
                        st.session_state.job_role
                    )


                st.session_state.feedback = (
                    feedback
                )


                score = extract_score(
                    feedback
                )


                if score is not None:

                    st.session_state.scores.append(
                        score
                    )


                st.rerun()


    # =====================================================
    # AI FEEDBACK
    # =====================================================

    if st.session_state.feedback:

        st.divider()

        st.markdown('<div class="section-label">AI COACH</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🤖 AI Feedback</div>', unsafe_allow_html=True)


        score = extract_score(
            st.session_state.feedback
        )


        if score is not None:
            status = "🌟 Excellent — interview-ready progress!" if score >= 8 else ("👍 Good — keep improving the weak areas." if score >= 6 else "💪 Keep practicing — you can improve this.")
            st.markdown(
                f'''
                <div class="score-card">
                    <div class="score-label">QUESTION SCORE</div>
                    <div class="score-number">{score:.1f}<span style="font-size:24px;color:#94a3b8;">/10</span></div>
                    <div class="score-status">{status}</div>
                </div>
                ''', unsafe_allow_html=True
            )

        clean_feedback = re.sub(r"<[^>]+>", "", st.session_state.feedback).strip()
        st.markdown(clean_feedback)


        st.divider()


        # =================================================
        # NEXT QUESTION
        # =================================================

        if current < total:

            if st.button(
                "➡️ Next Question",
                use_container_width=True
            ):

                next_number = current + 1


                with st.spinner(
                    "🤖 Gemma 3 is preparing "
                    "your next question..."
                ):

                    st.session_state.question = (
                        generate_question(
                            st.session_state.job_role,
                            st.session_state.experience,
                            st.session_state.category,
                            next_number
                        )
                    )


                st.session_state.question_number = (
                    next_number
                )

                st.session_state.answer = ""

                st.session_state.feedback = ""


                st.rerun()


        # =================================================
        # FINISH INTERVIEW
        # =================================================

        else:

            if st.button(
                "🏆 Finish Interview & View Report",
                use_container_width=True
            ):

                st.session_state.interview_finished = (
                    True
                )

                st.rerun()


    # =====================================================
    # END INTERVIEW
    # =====================================================

    st.divider()


    if st.button(
        "🛑 End Interview"
    ):

        reset_interview()

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown('<div class="footer">InterviewBuddy AI • Python • Streamlit • Ollama • Gemma 3 • Faster-Whisper</div>', unsafe_allow_html=True)