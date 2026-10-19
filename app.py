import streamlit as st
import imaplib
import email
from email.header import decode_header
import datetime

# --- Page Config ---
st.set_page_config(page_title="Email File Recovery", page_icon="📧")
st.title("📧 Email File Recovery Tool")
st.markdown("Recover attachments from your email account by filtering by date and keyword.")

# --- Sidebar Settings ---
st.sidebar.header("Connection Settings")
email_user = st.sidebar.text_input("Email Address")
email_pass = st.sidebar.text_input("App Password", type="password", help="Use the 16-character App Password, NOT your regular password.")

st.sidebar.header("Search Filters")
# Date filters to help find files from 2 years ago
start_date = st.sidebar.date_input("Start Date", value=datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.date(2023, 12, 31))
search_keyword = st.sidebar.text_input("Search Keyword (Optional)", placeholder="e.g. 'Photo' or 'Document'")

# Function to format date for IMAP (Format: DD-Mon-YYYY)
def format_date(date_obj):
    return date_obj.strftime("%d-%b-%Y")

if st.button("🔍 Start Recovery Scan"):
    if not email_user or not email_pass:
        st.error("Please provide both your email and app password in the sidebar.")
    else:
        try:
            with st.spinner("Connecting to server and scanning emails..."):
                # 1. Connect to Gmail IMAP server
                # Note: Use "imap.gmail.com" for Gmail or "imap-mail.outlook.com" for Outlook
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(email_user, email_pass)
                
                # Select the folder to search
                mail.select("INBOX") 

                # 2. Build the IMAP Search Query
                # Query format: (SINCE "date" BEFORE "date")
                query = f'(SINCE "{format_date(start_date)}" BEFORE "{format_date(end_date)}"'
                if search_keyword:
                    query += f' TEXT "{search_keyword}"'
                query += ')'

                status, messages = mail.search(None, query)
                email_ids = messages[0].split()

                if not email_ids:
                    st.warning("No emails found matching those criteria.")
                else:
                    st.success(f"Found {len(email_ids)} matching emails. Checking for attachments...")
                    
                    found_files = False
                    # 3. Loop through emails to find attachments
                    for e_id in email_ids:
                        res, msg_data = mail.fetch(e_id, "(RFC822)")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                subject = decode_header(msg["Subject"])[0][0]
                                if isinstance(subject, bytes):
                                    subject = subject.decode()

                                # Walk through the email parts
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
                                        
                                        # 4. Display result and download button
                                        with st.expander(f"📄 {decoded_filename} (Subject: {subject})"):
                                            st.download_button(
                                                label="Download File",
                                                data=part.get_payload(decode=True),
                                                file_name=decoded_filename,
                                                key=f"{e_id}_{decoded_filename}"
                                            )
                    
                    if not found_files:
                        st.info("Emails were found, but none of them had attachments.")
                
                mail.logout()
        except Exception as e:
            st.error(f"Connection failed: {e}")
            st.info("Tip: Make sure you are using an 'App Password' and that IMAP is enabled in your Gmail settings.")
