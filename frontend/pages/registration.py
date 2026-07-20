import re
import streamlit as st
from datetime import datetime


def show_registration_page():
    # ── Top bar ─────────────────────────────────────────────
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #030b1a 0%, #0c1e3d 100%);
        padding: 18px 36px;
        border-bottom: 1px solid #1a3050;
        display: flex; align-items: center; gap: 14px;
    ">
        <div style="
            width:40px;height:40px;
            background:linear-gradient(135deg,#1d4ed8,#0891b2);
            border-radius:10px;display:inline-flex;
            align-items:center;justify-content:center;font-size:20px;
        ">🛡️</div>
        <div>
            <div style="color:#f8fafc;font-weight:800;font-size:20px;letter-spacing:-0.3px;">
                InterviewGuard
            </div>
            <div style="color:#475569;font-size:11px;font-weight:500;letter-spacing:0.8px;
                text-transform:uppercase;">
                AI-Powered Interview Monitoring Platform
            </div>
        </div>
        <div style="margin-left:auto;color:#1e3a5f;font-size:12px;">
            """ + datetime.now().strftime("%A, %d %B %Y") + """
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero section ─────────────────────────────────────────
    st.markdown("""
    <div style="
        background: radial-gradient(ellipse at 50% 0%, #0c1e3d 0%, #050b17 60%);
        padding: 60px 20px 20px;
        text-align: center;
    ">
        <h1 style="font-size:38px;color:#f8fafc;margin:0 0 10px 0;letter-spacing:-1px;">
            Welcome to InterviewGuard
        </h1>
        <p style="color:#64748b;font-size:16px;margin:0;">
            Complete your registration to begin your AI-monitored technical interview.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Centered registration card ───────────────────────────
    _, card_col, _ = st.columns([1, 1.6, 1])

    with card_col:
        # Card border via HTML, widgets inside via Streamlit
        st.markdown("""
        <div style="
            background: linear-gradient(160deg, #0a1628 0%, #0d1b35 100%);
            border: 1px solid #1a3050;
            border-radius: 20px;
            padding: 40px 36px 28px;
            box-shadow: 0 30px 70px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.02);
            margin-bottom: 12px;
        ">
            <div style="margin-bottom:28px;">
                <div style="color:#f1f5f9;font-size:20px;font-weight:700;margin-bottom:4px;">
                    Candidate Registration
                </div>
                <div style="color:#475569;font-size:13px;">
                    All sessions are recorded and monitored by AI.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Form fields
        name = st.text_input("Candidate Name", placeholder="Enter your full name", key="reg_name")

        col_id, col_email = st.columns(2)
        with col_id:
            cid = st.text_input("Candidate ID", placeholder="e.g. CS2024001", key="reg_id")
        with col_email:
            email = st.text_input("Email (Optional)", placeholder="you@email.com", key="reg_email")

        role = st.selectbox("Interview Role", options=[
            "— Select a role —",
            "Full Stack Developer",
            "Software Engineer",
            "Backend Developer",
            "Frontend Developer",
            "Data Analyst",
            "Machine Learning Engineer",
            "Data Scientist",
            "DevOps Engineer",
            "Cloud Engineer",
            "Mobile Developer",
            "Cybersecurity Analyst",
        ], key="reg_role")

        # Inline error / success feedback
        error = st.session_state.get("reg_error")
        if error:
            st.error(f"⚠ {error}")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        col_val, col_start = st.columns([1, 2])

        with col_val:
            if st.button("Validate", use_container_width=True, key="btn_validate"):
                err = _validate(name, cid, role)
                st.session_state.reg_error = err
                if not err:
                    st.success("✓ All fields valid — ready to start.")

        with col_start:
            if st.button("Start Interview →", type="primary",
                         use_container_width=True, key="btn_start"):
                err = _validate(name, cid, role)
                if err:
                    st.session_state.reg_error = err
                    st.rerun()
                else:
                    st.session_state.reg_error = None
                    _launch_session(name.strip(), cid.strip(), email.strip(), role)

        # Info strip
        st.markdown("""
        <div style="
            margin-top:20px;
            padding:14px 18px;
            background:#060f1e;
            border:1px solid #0f2744;
            border-radius:10px;
            display:flex;gap:24px;
        ">
            <div style="color:#334155;font-size:12px;">
                🔒 <span style="color:#475569;">Session is private and secure</span>
            </div>
            <div style="color:#334155;font-size:12px;">
                📋 <span style="color:#475569;">20 randomised questions</span>
            </div>
            <div style="color:#334155;font-size:12px;">
                🤖 <span style="color:#475569;">AI monitoring active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _validate(name, cid, role) -> str:
    if not name or not name.strip():
        return "Candidate Name is required."
    if not cid or not cid.strip():
        return "Candidate ID is required."
    if not role or role.startswith("—"):
        return "Please select an Interview Role."
    return ""


def _launch_session(name, cid, email, role):
    from frontend.session_manager import InterviewSession
    from frontend.question_bank   import get_session_questions

    safe_name  = re.sub(r"[^\w]", "_", name)
    safe_id    = re.sub(r"[^\w]", "_", cid)
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id  = f"{safe_name}_{safe_id}"
    session_dir = f"reports/{session_id}_{timestamp}"

    candidate = {
        "name":        name,
        "id":          cid,
        "email":       email,
        "role":        role,
        "session_id":  session_id,
        "session_dir": session_dir,
    }

    with st.spinner("Initialising AI monitoring system..."):
        session = InterviewSession(candidate, session_dir)

    st.session_state.candidate        = candidate
    st.session_state.session          = session
    st.session_state.questions        = get_session_questions(20)
    st.session_state.q_index          = 0
    st.session_state.interview_active = True
    st.session_state.show_end_confirm = False
    st.session_state.reg_error        = ""
    st.session_state.page             = "interview"
    st.rerun()
