import streamlit as st

st.set_page_config(
    page_title="InterviewGuard — AI Interview Monitoring",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from frontend.style import inject_css
inject_css()

from frontend.pages.registration import show_registration_page
from frontend.pages.interview    import show_interview_page
from frontend.pages.completion   import show_completion_page

if "page" not in st.session_state:
    st.session_state.page = "registration"

{
    "registration": show_registration_page,
    "interview":    show_interview_page,
    "completion":   show_completion_page,
}.get(st.session_state.page, show_registration_page)()
