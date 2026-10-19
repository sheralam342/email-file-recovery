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

# Custom CSS to make the app look cleaner
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

# Professional Secret Handling: 
# It checks if you have a secrets.toml file. If not, it shows empty boxes.
default_email = st.secrets.get("EMAIL", "")
default_pass = st.secrets.get("APP_PASSWORD", "")

email_user = st.sidebar.text_input("Email Address", value=default_email)
email_pass = st.sidebar.text_input("App Password", value=default_pass, type="password", 
                                   help="Use the 16-character App Password from Google Settings.")

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
                
                # IMPORTANT: We select "[Gmail]/All Mail" to find sent, archived, and inbox items
                mail.select('"[Gmail]/All Mail"') 

                # 2. Build the IMAP Search Query
                query = f'(SINCE "{format_date(start_date)}" BEFORE "{format_date(end_date)}"'
                if search_keyword:
                    query += f' TEXT "{search_keyword}"'
                query += ')'

                status, messages = mail.search(None, query)
                email_ids = messages[0].split()

                if not email_ids:
                    st.warning("No emails found matching those criteria.")
                else:
                    st.success(f"Found {len(email_ids)} matching emails. Extracting attachments...")
                    
                    found_files = False
                    # 3. Loop through emails to find attachments
                    for e_id in email_ids:
                        res, msg_data = mail.fetch(e_id, "(RFC822)")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                
                                # Decode the email subject
                                subject_raw = msg.get("Subject", "No Subject")
                                subject = decode_header(subject_raw)[0][0]
                                if isinstance(subject, bytes):
                                    subject = subject.decode()

                                # Walk through the email parts to find files
                                for part in msg.walk():
                                    if part.get_content_maintype() == 'multipart':
                                        continue
                                    if part.get('Content-Disposition') is None:
                                        continue

                                    filename = part.get_filename()
                                    if filename:
                                        found_files = True
                                        # Decode filename
                                        decoded_filename = decode_header(filename)[0][0]
                                        if isinstance(decoded_filename, bytes):
                                            decoded_filename = decoded_filename.decode()
                                        
                                        # 4. Display results in professional expanders
                                        with st.expander(f"📄 {decoded_filename}"):
                                            st.write(f"**Subject:** {subject}")
                                            st.download_button(
                                                label="📥 Download File",
                                                data=part.get_payload(decode=True),
                                                file_name=decoded_filename,
                                                key=f"{e_id}_{decoded_filename}"
                                            )
                    
                    if not found_files:
                        st.info("Emails were found, but none of them contained physical attachments.")
                
                mail.logout()
        except Exception as e:
            st.error(f"Connection failed: {e}")
            st.info("Troubleshooting: Check if IMAP is enabled in Gmail settings and you are using an App Password.")

# --- Footer ---
st.divider()
st.caption("Developed as a Data Recovery Portfolio Project | Built with Python & Streamlit")
