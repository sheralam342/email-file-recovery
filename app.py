import streamlit as st
import imaplib
import email
from email.header import decode_header
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Email File Recovery Tool", 
    page_icon="📧", 
    layout="centered"
)

# Custom CSS for a professional LinkedIn-ready look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📧 Email File Recovery Tool")
st.markdown("""
**Professional tool to recover lost mobile files by scanning email attachments.**
This app connects to your email server and filters through your history to find files from a specific time period.
""")

# --- Sidebar: Connection Settings ---
st.sidebar.header("🔐 Connection Settings")

# Check for secrets.toml file for convenience
default_email = st.secrets.get("EMAIL", "")
default_pass = st.secrets.get("APP_PASSWORD", "")

# BOTH fields are now type="password" to hide them during screen recordings
email_user = st.sidebar.text_input(
    "Email Address", 
    value=default_email, 
    type="password", 
    help="Your email will be hidden for privacy."
)
email_pass = st.sidebar.text_input(
    "App Password", 
    value=default_pass, 
    type="password", 
    help="Use the 16-character App Password from Google Settings."
)

st.sidebar.divider()

# --- Sidebar: Search Filters ---
st.sidebar.header("🔍 Search Filters")

# Date filters to target files from 2 years ago
start_date = st.sidebar.date_input("Start Date", value=datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.date(2022, 12, 31))
search_keyword = st.sidebar.text_input("Search Keyword (Optional)", placeholder="e.g. 'Photos' or 'Work'")

# Helper function to format date for IMAP (Format: DD-Mon-YYYY)
def format_date(date_obj):
    return date_obj.strftime("%d-%b-%Y")

# --- Main Logic ---
if st.button("🚀 Start Recovery Scan"):
    if not email_user or not email_pass:
        st.error("Please provide both your email and app password in the sidebar.")
    else:
        try:
            with st.spinner("Connecting to secure server and scanning all mail folders..."):
                # 1. Connect to Gmail IMAP server
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(email_user, email_pass)
                
                # SELECT ALL MAIL: This finds sent, archived, and inbox items
                mail.select('"[Gmail]/All Mail"') 

                # 2. Build the IMAP Search Query
                query = f'(SINCE "{format_date(start_date)}" BEFORE "{format_date(end_date)}"'
                if search_keyword:
                    query += f' TEXT "{search_keyword}"'
                query += ')'

                status, messages = mail.search(None, query)
                email_ids =
