import time
import cv2
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# Streamlit 1.34+ Dialog for ending interview
@st.dialog("⚠ End Interview?")
def confirm_end_interview(session):
    st.write("This will stop the session and generate the final report.")
    st.write("This action cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Confirm End", type="primary", use_container_width=True):
            _end_interview(session)

def show_interview_page():
    session   = st.session_state.get("session")
    candidate = st.session_state.get("candidate", {})
    questions = st.session_state.get("questions", [])

    if not session or not questions:
        st.session_state.page = "registration"
        st.rerun()
        return

    q_idx = st.session_state.get("q_index", 0)

    # ── Header bar ───────────────────────────────────────────
    # Initial render shows 60:00 (1 hr). Javascript takes over instantly.
    h_left, h_center, h_right = st.columns([2, 3, 2])

    with h_left:
        st.markdown("""
        <div style="padding:14px 20px;display:flex;align-items:center;gap:10px;">
            <div style="
                width:32px;height:32px;
                background:#0ea5e9;
                border-radius:8px;display:inline-flex;
                align-items:center;justify-content:center;font-size:16px;">🛡️
            </div>
            <span style="color:#f8fafc;font-weight:800;font-size:16px;">InterviewGuard</span>
        </div>
        """, unsafe_allow_html=True)

    with h_center:
        st.markdown(f"""
        <div style="padding:14px;text-align:center;">
            <span style="color:#f1f5f9;font-weight:700;font-size:15px;">
                {candidate.get('name','')}
            </span>
            <span style="color:#334155;margin:0 10px;">│</span>
            <span style="color:#94a3b8;font-size:13px;">{candidate.get('role','')}</span>
            <span style="color:#334155;margin:0 10px;">│</span>
            <span style="color:#64748b;font-size:12px;">ID: {candidate.get('id','')}</span>
        </div>
        """, unsafe_allow_html=True)

    with h_right:
        st.markdown(f"""
        <div style="padding:14px;text-align:right;display:flex;
            align-items:center;justify-content:flex-end;gap:16px;">
            <span id="interview-timer" style="
                color:#0ea5e9;font-weight:700;font-size:18px;
                font-variant-numeric:tabular-nums;letter-spacing:1px;">
                ⏱ 60:00
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Thin separator line
    st.markdown("""
    <div style="height:1px;
        background:linear-gradient(90deg,transparent 0%,#334155 30%,#334155 70%,transparent 100%);
        margin-bottom:16px;">
    </div>
    """, unsafe_allow_html=True)

    # ── Main two-column layout (70/30) ───────────────────────────────
    question_col, webcam_col = st.columns([7, 3], gap="large")

    with question_col:
        _render_question_card(questions, q_idx)

    with webcam_col:
        _render_webcam()
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("🏁  End Interview", use_container_width=True, key="btn_end"):
            confirm_end_interview(session)


    # ── Javascript Injection for Timer and Shortcuts ─────────────
    # Timer Logic: 1 Hour Countdown
    components.html(f"""
    <script>
    const doc = window.parent.document;
    
    let start_time = {session.session_start};
    let total_duration = 3600; // 1 hour in seconds
    
    setInterval(() => {{
        let now = Date.now() / 1000;
        let elapsed = Math.floor(now - start_time);
        let remaining = Math.max(0, total_duration - elapsed);
        
        let m = Math.floor(remaining / 60).toString().padStart(2, '0');
        let s = (remaining % 60).toString().padStart(2, '0');
        
        let timer_el = doc.getElementById('interview-timer');
        if (timer_el) timer_el.innerText = '⏱ ' + m + ':' + s;
    }}, 1000);
    
    // Keyboard shortcuts
    doc.addEventListener('keydown', function(e) {{
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        let label = '';
        if (e.key === 'ArrowRight') label = 'Next';
        if (e.key === 'ArrowLeft')  label = 'Previous';
        if (e.key === 'Escape')     label = 'End Interview';
        if (!label) return;
        doc.querySelectorAll('button').forEach(btn => {{
            if (btn.textContent.includes(label) && !btn.disabled) btn.click();
        }});
    }});
    </script>
    """, height=0)


# ─────────────────────────────────────────────────────────────


def _render_webcam():
    st.markdown("""
<div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:12px;">
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
        <div style="width:6px;height:6px;background:#22c55e;border-radius:50%;box-shadow:0 0 8px #22c55e55;"></div>
        <span style="color:#94a3b8;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;">Live</span>
        <span style="margin-left:auto;color:#64748b;font-size:9px;">AI Monitoring</span>
    </div>
    <div style="background:#020617;border:1px solid #0f172a;border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center;min-height:180px;">
        <img src="http://localhost:8502/video_feed" style="width:100%;height:auto;object-fit:cover;" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100%\\' height=\\'180\\'><rect width=\\'100%\\' height=\\'100%\\' fill=\\'#020617\\'/><text x=\\'50%\\' y=\\'50%\\' dominant-baseline=\\'middle\\' text-anchor=\\'middle\\' fill=\\'#334155\\' font-size=\\'12\\'>Camera Offline</text></svg>';" />
    </div>
</div>
    """, unsafe_allow_html=True)


def _render_question_card(questions: list, q_idx: int):
    total    = len(questions)
    progress = (q_idx + 1) / total

    # Card top section
    st.markdown(f"""
    <div style="
        background:#1e293b;
        border:1px solid #334155;
        border-radius:16px 16px 0 0;
        padding:20px 24px 14px;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="
                background:rgba(14,165,233,0.15);
                border:1px solid rgba(14,165,233,0.3);
                color:#38bdf8;
                padding:4px 14px;border-radius:20px;
                font-size:11px;font-weight:700;letter-spacing:0.8px;
            ">QUESTION {q_idx + 1} / {total}</span>
            <span style="color:#64748b;font-size:11px;">
                {total - q_idx - 1} remaining
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    st.progress(progress)

    # Question text
    st.markdown(f"""
    <div style="
        background:#0f172a;
        border-left:1px solid #334155;
        border-right:1px solid #334155;
        border-bottom:1px solid #334155;
        padding:24px;
    ">
        <p style="
            color:#f8fafc !important;
            font-size:17px;
            line-height:1.75;
            margin:0 0 20px 0;
            font-weight:500;
        ">{questions[q_idx]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive input area - Native Streamlit elements
    st.text_area(
        "Your Answer", 
        placeholder="Type your answer or code here... (Optional)", 
        height=150, 
        key=f"q_{q_idx}",
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="
        background:#1e293b;
        border:1px solid #334155;
        border-top:none;
        border-radius:0 0 16px 16px;
        padding:8px 24px 16px;
    "></div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Navigation buttons
    prev_col, _, next_col = st.columns([1, 4, 1])

    with prev_col:
        if st.button("← Previous", use_container_width=True,
                     key="btn_prev", disabled=(q_idx == 0)):
            st.session_state.q_index = max(0, q_idx - 1)
            st.rerun()

    with next_col:
        if st.button("Next →", type="primary", use_container_width=True,
                     key="btn_next", disabled=(q_idx == total - 1)):
            st.session_state.q_index = min(total - 1, q_idx + 1)
            st.rerun()


def _end_interview(session):
    st.session_state.interview_active = False
    
    with st.spinner("Closing session..."):
        session.stop()

    with st.spinner("Generating reports..."):
        paths = session.generate_reports()

    st.session_state.report_paths = paths
    st.session_state.page = "completion"
    st.rerun()
