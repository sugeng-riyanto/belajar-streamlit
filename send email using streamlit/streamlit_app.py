import streamlit as st
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

FLASK_API_URL = "http://127.0.0.1:5001/api/emails"

# Function to get all emails
def get_emails():
    response = requests.get(FLASK_API_URL)
    return response.json()

# Function to add a new email
def add_email(name, email, fee, virtual_account):
    user = {"name": name, "email": email, "fee": fee, "virtual_account": virtual_account}
    response = requests.post(FLASK_API_URL, json=user)
    return response.json()

# Function to send email
def send_email(to_email, name, fee, virtual_account):
    from_email = "shsmodernhill@shb.sch.id"
    from_password = "jvvmdgxgdyqflcrf"
    subject = "Payment Details"

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ padding: 20px; background-color: #f9f9f9; }}
            .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
            .content {{ margin-top: 20px; }}
            .footer {{ margin-top: 20px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Payment Details</h1>
            </div>
            <div class="content">
                <p>Dear {name},</p>
                <p>Please find below your payment details:</p>
                <p><strong>Fee:</strong> ${fee}</p>
                <p><strong>Virtual Account:</strong> {virtual_account}</p>
                <p>Thank you!</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Your Company</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

# Streamlit UI
st.title("Email Blaster with Streamlit, Flask, and SQLite")

menu = ["Add Email", "View Emails", "Send Emails"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Email":
    st.subheader("Add New Email")
    name = st.text_input("Name")
    email = st.text_input("Email")
    fee = st.number_input("Fee", min_value=0.0)
    virtual_account = st.text_input("Virtual Account")
    if st.button("Add Email"):
        add_email(name, email, fee, virtual_account)
        st.success(f"Email for '{name}' added successfully!")

elif choice == "View Emails":
    st.subheader("View All Emails")
    emails = get_emails()
    for email in emails:
        st.write(f"ID: {email[0]}, Name: {email[1]}, Email: {email[2]}, Fee: {email[3]}, Virtual Account: {email[4]}")

elif choice == "Send Emails":
    st.subheader("Send Emails to All Users")
    emails = get_emails()
    if st.button("Send Emails"):
        for email in emails:
            send_email(email[2], email[1], email[3], email[4])
        st.success("Emails sent successfully!")

# Custom HTML and CSS
st.markdown("""
    <style>
    .stButton>button {
        color: white;
        background-color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)
