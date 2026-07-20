import os
import streamlit as st
from datetime import datetime


def show_completion_page():
    candidate    = st.session_state.get("candidate", {})
    report_paths = st.session_state.get("report_paths", {})
    pdf_path     = report_paths.get("pdf_path", "")
    json_path    = report_paths.get("json_path", "")

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style="
        background:#0f172a;
        padding:18px 36px;
        border-bottom:1px solid #1e293b;
        display:flex;align-items:center;gap:12px;
    ">
        <div style="
            width:32px;height:32px;
            background:#0ea5e9;
            border-radius:8px;display:inline-flex;
            align-items:center;justify-content:center;font-size:16px;">🛡️
        </div>
        <span style="color:#f8fafc;font-weight:800;font-size:17px;">InterviewGuard</span>
        <span style="margin-left:auto;color:#64748b;font-size:12px;">
            Session Complete — """ + datetime.now().strftime("%d %b %Y, %H:%M") + """
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Centered completion card ─────────────────────────────
    _, center, _ = st.columns([1, 1.8, 1])

    with center:
        st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

        # Success banner
        st.markdown(f"""
        <div style="
            background:#1e293b;
            border:1px solid #334155;
            border-radius:20px;
            padding:48px 40px 36px;
            text-align:center;
            box-shadow:0 30px 70px rgba(0,0,0,0.55);
        ">
            <!-- Check icon -->
            <div style="
                width:72px;height:72px;margin:0 auto 20px;
                background:#022c22;
                border:2px solid #10b981;
                border-radius:50%;display:flex;
                align-items:center;justify-content:center;
                font-size:30px;
            ">✓</div>

            <h2 style="color:#f8fafc;font-size:26px;margin:0 0 6px;">
                Interview Completed
            </h2>
            <p style="color:#94a3b8;font-size:14px;margin:0 0 32px;">
                {candidate.get('name','Candidate')} &nbsp;·&nbsp; {candidate.get('role','')}
                &nbsp;·&nbsp; ID: {candidate.get('id','')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Download buttons ──────────────────────────────────
        dl_pdf, dl_json = st.columns(2)

        with dl_pdf:
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📄  Download PDF Report",
                        data=f.read(),
                        file_name=f"InterviewGuard_{candidate.get('id','report')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="dl_pdf"
                    )
            else:
                st.markdown("""
                <div style="color:#334155;font-size:12px;text-align:center;padding:10px;">
                    PDF not available
                </div>""", unsafe_allow_html=True)

        with dl_json:
            if json_path and os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        "📋  Download JSON Report",
                        data=f.read(),
                        file_name=f"InterviewGuard_{candidate.get('id','report')}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="dl_json"
                    )
            else:
                st.markdown("""
                <div style="color:#334155;font-size:12px;text-align:center;padding:10px;">
                    JSON not available
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if st.button("🔄  Start New Interview", use_container_width=True, key="btn_new"):
            _reset_and_restart()


def _reset_and_restart():
    keys = [
        "candidate", "session", "questions", "q_index",
        "interview_active", "show_end_confirm", "report_paths",
        "reg_error", "reg_name", "reg_id", "reg_email", "reg_role",
    ]
    for k in keys:
        st.session_state.pop(k, None)

    st.session_state.page = "registration"
    st.rerun()
