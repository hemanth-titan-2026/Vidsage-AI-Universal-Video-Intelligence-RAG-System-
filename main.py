import streamlit as st
import sys
import os
import base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.video_processor import process_video
from app.rag_engine import build_rag, ask_question

# ── PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="VidSage AI — by Pragya-X",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── LOGO HELPER ──────────────────────────────────────────────────
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pragya_x_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:32px; object-fit:contain;" />' if logo_b64 else '<span style="color:#ff0000;font-weight:900;font-size:1.1rem;">PRAGYA-X</span>'

# ── PREMIUM CSS ──────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    /* ── Base ── */
    .stApp {{
        background: #0a0a0a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #f1f5f9;
    }}

    .main .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-track {{ background: #111; }}
    ::-webkit-scrollbar-thumb {{ background: #ff0000; border-radius: 2px; }}

    /* ══════════════════════════════════════════
       NAVBAR
    ══════════════════════════════════════════ */
    .navbar {{
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(10,10,10,0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 0.9rem 2.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .navbar-left {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}

    .navbar-logo {{ height: 32px; object-fit: contain; }}

    .navbar-divider {{
        width: 1px;
        height: 24px;
        background: rgba(255,255,255,0.12);
    }}

    .navbar-product {{
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.3px;
    }}

    .navbar-product span {{
        color: #ff0000;
    }}

    .navbar-right {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .nav-badge {{
        background: rgba(255,0,0,0.1);
        border: 1px solid rgba(255,0,0,0.25);
        color: #ff4444;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}

    .nav-badge-gray {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        color: #64748b;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 500;
    }}

    /* ══════════════════════════════════════════
       HERO
    ══════════════════════════════════════════ */
    .hero {{
        text-align: center;
        padding: 4rem 2rem 2.5rem;
        position: relative;
        overflow: hidden;
    }}

    .hero::before {{
        content: '';
        position: absolute;
        top: -60px;
        left: 50%;
        transform: translateX(-50%);
        width: 600px;
        height: 300px;
        background: radial-gradient(ellipse, rgba(255,0,0,0.08) 0%, transparent 70%);
        pointer-events: none;
    }}

    .hero-eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255,0,0,0.08);
        border: 1px solid rgba(255,0,0,0.2);
        color: #ff6666;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }}

    .hero-title {{
        font-size: clamp(2.8rem, 6vw, 4.5rem);
        font-weight: 900;
        letter-spacing: -2px;
        line-height: 1.05;
        color: #ffffff;
        margin-bottom: 1rem;
    }}

    .hero-title .red {{ color: #ff0000; }}

    .hero-subtitle {{
        font-size: 1.1rem;
        color: #64748b;
        font-weight: 400;
        max-width: 520px;
        margin: 0 auto 2rem;
        line-height: 1.6;
    }}

    .hero-chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        justify-content: center;
        margin-bottom: 0.5rem;
    }}

    .chip {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        color: #94a3b8;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        transition: all 0.2s;
    }}

    /* ══════════════════════════════════════════
       STATS
    ══════════════════════════════════════════ */
    .stats-row {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        padding: 0 2.5rem 2rem;
    }}

    .stat-card {{
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }}

    .stat-card:hover {{
        background: rgba(255,0,0,0.04);
        border-color: rgba(255,0,0,0.15);
        transform: translateY(-2px);
    }}

    .stat-num {{
        font-size: 1.9rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -1px;
    }}

    .stat-num.red {{ color: #ff0000; }}

    .stat-label {{
        font-size: 0.75rem;
        color: #475569;
        font-weight: 500;
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ══════════════════════════════════════════
       MAIN PANEL
    ══════════════════════════════════════════ */
    .panel-wrapper {{
        display: grid;
        grid-template-columns: 420px 1fr;
        gap: 1.5rem;
        padding: 0 2.5rem 2.5rem;
        min-height: 600px;
    }}

    .panel {{
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 20px;
        padding: 1.75rem;
        position: relative;
        overflow: hidden;
    }}

    .panel::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #ff0000, #ff4444, transparent);
        border-radius: 20px 20px 0 0;
    }}

    .panel-title {{
        font-size: 0.7rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .panel-title::after {{
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.05);
    }}

    /* ══════════════════════════════════════════
       INPUT FIELDS
    ══════════════════════════════════════════ */
    .stTextInput > div > div > input {{
        background: rgba(255,255,255,0.04) !important;
        border: 1.5px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: #ff0000 !important;
        box-shadow: 0 0 0 3px rgba(255,0,0,0.08) !important;
        background: rgba(255,0,0,0.03) !important;
    }}

    .stTextInput > div > div > input::placeholder {{
        color: #334155 !important;
    }}

    /* ══════════════════════════════════════════
       RADIO
    ══════════════════════════════════════════ */
    .stRadio > div {{
        display: flex;
        gap: 0.5rem;
        flex-direction: row !important;
    }}

    .stRadio label {{
        color: #64748b !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* ══════════════════════════════════════════
       BUTTON
    ══════════════════════════════════════════ */
    .stButton > button {{
        background: linear-gradient(135deg, #ff0000, #cc0000) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(255,0,0,0.25) !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(255,0,0,0.4) !important;
        background: linear-gradient(135deg, #ff1a1a, #dd0000) !important;
    }}

    .stButton > button:active {{
        transform: translateY(0) !important;
    }}

    /* ══════════════════════════════════════════
       HOW IT WORKS STEPS
    ══════════════════════════════════════════ */
    .step {{
        display: flex;
        align-items: flex-start;
        gap: 0.85rem;
        margin-bottom: 0.9rem;
    }}

    .step-num {{
        width: 26px;
        height: 26px;
        min-width: 26px;
        background: rgba(255,0,0,0.1);
        border: 1px solid rgba(255,0,0,0.25);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 800;
        color: #ff4444;
    }}

    .step-text {{
        font-size: 0.85rem;
        color: #64748b;
        line-height: 1.5;
        padding-top: 0.2rem;
    }}

    .step-text strong {{ color: #94a3b8; font-weight: 600; }}

    /* ══════════════════════════════════════════
       TRANSCRIPT
    ══════════════════════════════════════════ */
    .transcript-box {{
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1rem;
        font-size: 0.82rem;
        color: #64748b;
        line-height: 1.7;
        max-height: 160px;
        overflow-y: auto;
        margin-top: 0.75rem;
    }}

    .word-count {{
        font-size: 0.75rem;
        color: #334155;
        text-align: right;
        margin-top: 0.4rem;
    }}

    /* ══════════════════════════════════════════
       CHAT PANEL
    ══════════════════════════════════════════ */
    .chat-empty {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
        gap: 1rem;
    }}

    .chat-empty-icon {{
        font-size: 3.5rem;
        opacity: 0.3;
    }}

    .chat-empty-text {{
        color: #334155;
        font-size: 1rem;
        font-weight: 500;
        text-align: center;
    }}

    .chat-empty-sub {{
        color: #1e293b;
        font-size: 0.82rem;
        text-align: center;
    }}

    /* Chat messages */
    [data-testid="stChatMessage"] {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
        padding: 0.9rem 1.1rem !important;
        margin-bottom: 0.6rem !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Chat input */
    [data-testid="stChatInputContainer"] {{
        background: rgba(255,255,255,0.04) !important;
        border: 1.5px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        margin-top: 1rem !important;
    }}

    [data-testid="stChatInputContainer"]:focus-within {{
        border-color: #ff0000 !important;
        box-shadow: 0 0 0 3px rgba(255,0,0,0.08) !important;
    }}

    /* ══════════════════════════════════════════
       ALERTS
    ══════════════════════════════════════════ */
    .stSuccess > div {{
        background: rgba(34,197,94,0.06) !important;
        border: 1px solid rgba(34,197,94,0.2) !important;
        border-radius: 12px !important;
        color: #4ade80 !important;
        font-family: 'Inter', sans-serif !important;
    }}

    .stError > div {{
        background: rgba(239,68,68,0.06) !important;
        border: 1px solid rgba(239,68,68,0.2) !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Spinner */
    .stSpinner > div {{
        border-top-color: #ff0000 !important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        color: #64748b !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
    }}

    /* ══════════════════════════════════════════
       FOOTER
    ══════════════════════════════════════════ */
    .footer {{
        border-top: 1px solid rgba(255,255,255,0.05);
        padding: 2rem 2.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }}

    .footer-left {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .footer-right {{
        color: #1e293b;
        font-size: 0.75rem;
        text-align: right;
        line-height: 1.6;
    }}

    .footer-tagline {{
        color: #ff0000;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.2rem;
    }}

    /* ══════════════════════════════════════════
       SECTION DIVIDER
    ══════════════════════════════════════════ */
    .section-divider {{
        height: 1px;
        background: rgba(255,255,255,0.05);
        margin: 0 2.5rem 2rem;
    }}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────
for key, default in {
    "qa_chain": None,
    "transcript": None,
    "chat_history": [],
    "video_processed": False,
    "questions_asked": 0,
    "show_transcript": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="navbar">
    <div class="navbar-left">
        {logo_html}
        <div class="navbar-divider"></div>
        <div class="navbar-product">Vid<span>Sage</span> AI</div>
    </div>
    <div class="navbar-right">
        <span class="nav-badge">⚡ Groq Powered</span>
        <span class="nav-badge-gray">🦙 LLaMA 3.3 70B</span>
        <span class="nav-badge-gray">v1.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">🎬 &nbsp; Multimodal AI · RAG Pipeline · Real-time Q&A</div>
    <div class="hero-title">Ask Anything.<br/><span class="red">About Any Video.</span></div>
    <div class="hero-subtitle">
        Paste a YouTube link, upload a video, or drop any URL.
        VidSage AI extracts, understands, and answers — instantly.
    </div>
    <div class="hero-chips">
        <span class="chip">🎙️ Whisper Transcription</span>
        <span class="chip">🔍 Vector Search</span>
        <span class="chip">⚡ Sub-second Retrieval</span>
        <span class="chip">🌐 Any Video Source</span>
        <span class="chip">💬 Multi-turn Chat</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# STATS
# ══════════════════════════════════════════════════════════════════
videos = 1 if st.session_state.video_processed else 0
questions = st.session_state.questions_asked

st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-num">∞</div>
        <div class="stat-label">Video Sources</div>
    </div>
    <div class="stat-card">
        <div class="stat-num {'red' if videos else ''}">{videos}</div>
        <div class="stat-label">Videos Loaded</div>
    </div>
    <div class="stat-card">
        <div class="stat-num {'red' if questions else ''}">{questions}</div>
        <div class="stat-label">Questions Asked</div>
    </div>
    <div class="stat-card">
        <div class="stat-num red">70B</div>
        <div class="stat-label">Model Params</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MAIN TWO-COLUMN LAYOUT
# ══════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1, 1.6], gap="large")

# ── LEFT PANEL ───────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="panel-title">📥 &nbsp; Video Input</div>', unsafe_allow_html=True)

    input_type = st.radio(
        "",
        ["🎥 YouTube URL", "🔗 Any Video URL"],
        horizontal=True,
        label_visibility="collapsed"
    )

    video_url = st.text_input(
        "",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )

    process_btn = st.button("▶  Process Video", type="primary")
    if process_btn:
        if not video_url.strip():
            st.error("⚠️ Please enter a video URL first.")
        else:
            with st.spinner("⬇️ Downloading & transcribing audio..."):
                try:
                    # Reset previous video session completely
                    st.session_state.qa_chain = None
                    st.session_state.transcript = None
                    st.session_state.chat_history = []
                    st.session_state.video_processed = False
                    st.session_state.questions_asked = 0
                    st.session_state.show_transcript = False
                    # Process new video
                    transcript = process_video(video_url)
                    st.session_state.transcript = transcript
                    with st.spinner("🧠 Building RAG knowledge base..."):
                        qa_chain = build_rag(transcript)
                        st.session_state.qa_chain = qa_chain
                        st.session_state.video_processed = True
                    st.success("✅ New video ready! Ask your first question →")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    # Transcript
    if st.session_state.transcript:
        with st.expander("📄 View Transcript"):
            txt = st.session_state.transcript
            display = txt[:2000] + "..." if len(txt) > 2000 else txt
            st.markdown(f'<div class="transcript-box">{display}</div>', unsafe_allow_html=True)
            word_count = len(txt.split())
            st.markdown(f'<div class="word-count">📝 {word_count:,} words</div>', unsafe_allow_html=True)

    # How it works
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div class="panel-title">⚙️ &nbsp; How It Works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="step">
        <div class="step-num">1</div>
        <div class="step-text"><strong>Download</strong> — yt-dlp fetches audio from any video source</div>
    </div>
    <div class="step">
        <div class="step-num">2</div>
        <div class="step-text"><strong>Transcribe</strong> — OpenAI Whisper converts speech to text</div>
    </div>
    <div class="step">
        <div class="step-num">3</div>
        <div class="step-text"><strong>Embed</strong> — LangChain chunks & stores in ChromaDB</div>
    </div>
    <div class="step">
        <div class="step-num">4</div>
        <div class="step-text"><strong>Answer</strong> — LLaMA 3.3 70B retrieves & responds via Groq</div>
    </div>
    """, unsafe_allow_html=True)

# ── RIGHT PANEL ──────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="panel-title">💬 &nbsp; AI Chat</div>', unsafe_allow_html=True)

    if not st.session_state.qa_chain:
        st.markdown("""
        <div class="chat-empty">
            <div class="chat-empty-icon">🎬</div>
            <div class="chat-empty-text">No video loaded yet</div>
            <div class="chat-empty-sub">Paste a video URL on the left and hit Process<br/>to start asking questions</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Chat history
        chat_area = st.container(height=430)
        with chat_area:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style="text-align:center; padding:3rem 1rem; color:#334155;">
                    <div style="font-size:2rem; margin-bottom:0.75rem;">💡</div>
                    <div style="font-size:0.9rem;">Video loaded! Ask your first question below.</div>
                </div>
                """, unsafe_allow_html=True)
            for chat in st.session_state.chat_history:
                with st.chat_message("user", avatar="👤"):
                    st.write(chat["question"])
                with st.chat_message("assistant", avatar="🎬"):
                    st.write(chat["answer"])

        # Chat input
        question = st.chat_input("Ask anything about the video...")
        if question:
            with st.spinner("🤔 Thinking..."):
                answer = ask_question(st.session_state.qa_chain, question)
            st.session_state.chat_history.append({
                "question": question,
                "answer": answer
            })
            st.session_state.questions_asked += 1
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="footer">
    <div class="footer-left">
        {logo_html}
        <div>
            <div style="color:#94a3b8; font-size:0.82rem; font-weight:600;">
                VidSage AI &nbsp;·&nbsp; A Pragya-X Product
            </div>
            <div class="footer-tagline">Transforming Businesses with AI</div>
        </div>
    </div>
    <div class="footer-right">
        Built by <span style="color:#94a3b8; font-weight:600;">Hemanth Kumar</span><br/>
        Powered by Groq &nbsp;·&nbsp; LLaMA 3.3 70B &nbsp;·&nbsp; OpenAI Whisper &nbsp;·&nbsp; LangChain
    </div>
</div>
""", unsafe_allow_html=True)