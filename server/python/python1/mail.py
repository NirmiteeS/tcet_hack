import smtplib
import streamlit as st
import google.generativeai as genai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import pandas as pd
import re

# Email credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "crce.10408.ce@gmail.com"
SENDER_PASSWORD = "veqd ugtd hazz nycl"

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyC5kiR_7pP0x1ft-Fd2mqgakXwl_D7-Kl0"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-pro")

# Initialize session state
if 'generated_emails' not in st.session_state:
    st.session_state.generated_emails = []
if 'generated_subjects' not in st.session_state:
    st.session_state.generated_subjects = []
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

def convert_to_html(text):
    """Convert plain text to HTML with proper formatting"""
    # Replace newlines with HTML breaks
    text = text.replace('\n', '<br>')
    # Add paragraph tags
    paragraphs = text.split('<br><br>')
    text = ''.join(f'<p style="margin-bottom: 15px;">{p}</p>' for p in paragraphs)
    # Style the entire email
    html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;">
        {text}
    </div>
    """
    return html

def send_email(to_email, subject, body):
    """Send an email using smtplib."""
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Convert body to HTML with proper formatting
        html_body = convert_to_html(body)
        msg.attach(MIMEText(html_body, "html"))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
            
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Streamlit UI
st.subheader("Email Sender with Gemini API")
st.markdown("Generate and customize email content")

# Email Mode Selection
email_mode = st.radio("Select Email Mode", ["Single Email", "Bulk Email from CSV"])

if email_mode == "Single Email":
    # Single email input
    to_email = st.text_input("Recipient Email")
    body_idea = st.text_area("Enter the idea for the email")

else:
    uploaded_file = st.file_uploader("Upload CSV file with email addresses", type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.csv_data = df
            st.success(f"CSV loaded with {len(df)} recipients")
            st.write("Preview of CSV data:")
            st.write(df.head())
            required_cols = ['email']
            if not all(col in df.columns for col in required_cols):
                st.error("CSV must contain 'email' column")
                st.session_state.csv_data = None
        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")
            st.session_state.csv_data = None
    
    body_idea = st.text_area("Enter the template idea for bulk emails")

# Generate new email option
if st.button("Generate New Option"):
    if (email_mode == "Single Email" and to_email and body_idea) or \
       (email_mode == "Bulk Email from CSV" and st.session_state.csv_data is not None and body_idea):
        with st.spinner("Generating email content..."):
            try:
                # Generate subject and body
                subject_prompt = f"Generate a professional and relevant subject line for an email with the following idea: {body_idea}"
                body_prompt = f"Generate a professional email body based on the following idea: {body_idea}. Include placeholder text in [square brackets] for customizable fields. Ensure proper formatting with paragraphs and spacing."
                
                subject_response = model.generate_content(subject_prompt)
                body_response = model.generate_content(body_prompt)
                
                subject = subject_response.text.strip()
                email_body = body_response.text.strip()
                
                st.session_state.generated_subjects.append(subject)
                st.session_state.generated_emails.append(email_body)
                st.success("New email option generated!")
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
    else:
        st.error("Please fill in all required fields")

# Display all generated options
if st.session_state.generated_emails:
    st.subheader("Generated Email Options")
    for i, (subject, email) in enumerate(zip(st.session_state.generated_subjects, st.session_state.generated_emails)):
        with st.expander(f"Option {i + 1}"):
            st.subheader("Subject")
            edited_subject = st.text_input(f"Edit subject {i + 1}", subject, key=f"subject_{i}")
            st.subheader("Body")
            edited_email = st.text_area(f"Edit email body {i + 1}", email, height=200, key=f"email_{i}")
            if st.button(f"Select Option {i + 1}", key=f"select_{i}"):
                st.session_state.selected_subject = edited_subject
                st.session_state.selected_email = edited_email
                st.success(f"Option {i + 1} selected for sending")

# Clear options button
if st.session_state.generated_emails:
    if st.button("Clear All Options"):
        st.session_state.generated_emails = []
        st.session_state.generated_subjects = []
        st.session_state.selected_email = None
        st.session_state.selected_subject = None
        st.success("All options cleared!")

# Send selected email
if st.session_state.selected_email:
    st.subheader("Selected Email Content")
    st.text("Subject: " + st.session_state.selected_subject)
    
    final_email = st.text_area(
        "Make final edits before sending",
        st.session_state.selected_email,
        height=300
    )
    
    if st.button("Send Email"):
        with st.spinner("Sending email..."):
            if email_mode == "Single Email":
                # Send single email
                if send_email(to_email, st.session_state.selected_subject, final_email):
                    st.success(f"✅ Email sent successfully to {to_email}")
                    time.sleep(1)
            else:
                # Send bulk emails
                if st.session_state.csv_data is not None:
                    successful_sends = 0
                    failed_sends = 0
                    progress_bar = st.progress(0)
                    
                    for index, row in st.session_state.csv_data.iterrows():
                        recipient_email = row['email']
                        try:
                            if send_email(recipient_email, st.session_state.selected_subject, final_email):
                                successful_sends += 1
                            else:
                                failed_sends += 1
                        except Exception as e:
                            failed_sends += 1
                            st.error(f"Failed to send to {recipient_email}: {str(e)}")
                        
                        # Update progress
                        progress = (index + 1) / len(st.session_state.csv_data)
                        progress_bar.progress(progress)
                        time.sleep(0.1)  # Small delay to prevent rate limiting
                    
                    st.success(f"✅ Bulk email campaign completed!\nSuccessful: {successful_sends}\nFailed: {failed_sends}")
                
            # Clear the form after successful send
            st.session_state.selected_email = None
            st.session_state.selected_subject = None
            st.session_state.generated_emails = []
            st.session_state.generated_subjects = []

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)