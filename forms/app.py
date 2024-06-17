import streamlit as st
import sqlite3
import pandas as pd
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from fpdf import FPDF
import io

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id TEXT PRIMARY KEY,
            user_name TEXT,
            user_signature TEXT,
            user_score INTEGER,
            second_user_name TEXT,
            second_user_signature TEXT,
            second_user_score INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    # Inserting a default admin user for demonstration purposes
    c.execute('''
        INSERT OR IGNORE INTO admins (username, password)
        VALUES (?, ?)
    ''', ('admin', 'password'))
    conn.commit()
    conn.close()

def generate_unique_link():
    unique_id = str(uuid.uuid4())
    return f"http://localhost:8501/?id={unique_id}", unique_id

def save_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO forms (id, user_name, user_signature, user_score, second_user_name, second_user_signature, second_user_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (unique_id, data.get('user_name'), data.get('user_signature'), data.get('user_score'),
          data.get('second_user_name'), data.get('second_user_signature'), data.get('second_user_score')))
    conn.commit()
    conn.close()

def get_data(unique_id):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM forms WHERE id = ?', (unique_id,))
    data = c.fetchone()
    conn.close()
    if data:
        return {
            'id': data[0],
            'user_name': data[1],
            'user_signature': data[2],
            'user_score': data[3],
            'second_user_name': data[4],
            'second_user_signature': data[5],
            'second_user_score': data[6]
        }
    return None

def get_all_data():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM forms')
    data = c.fetchall()
    conn.close()
    return data

def update_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        UPDATE forms
        SET second_user_name = ?, second_user_signature = ?, second_user_score = ?
        WHERE id = ?
    ''', (data.get('second_user_name'), data.get('second_user_signature'), data.get('second_user_score'), unique_id))
    conn.commit()
    conn.close()

def send_email(to_email, link):
    from_email = 'shsmodernhill@shb.sch.id'
    from_password = 'jvvmdgxgdyqflcrf' 
    
    subject = "Complete the Form"
    body = f"Please complete the form by clicking the following link: {link}"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    
    pdf.cell(200, 10, txt = "Form Response", ln = True, align = 'C')
    
    for key, value in data.items():
        pdf.cell(200, 10, txt = f"{key}: {value}", ln = True, align = 'L')
    
    return pdf.output(dest='S').encode('latin1')

def sign_up(username, password):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def send_pdf_via_email(to_email, pdf_data, pdf_filename):
    from_email = 'shsmodernhill@shb.sch.id'
    from_password = 'jvvmdgxgdyqflcrf'
    
    subject = "Form Response PDF"
    body = "Please find the attached PDF containing the form response."
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    attachment = MIMEApplication(pdf_data, _subtype="pdf")
    attachment.add_header('content-disposition', 'attachment', filename=pdf_filename)
    msg.attach(attachment)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False

# Home page
def home():
    st.title("User Signature and Data Form")

    # Check if this is the second part of the form based on URL parameters
    query_params = st.query_params
    if "id" in query_params:
        unique_id = query_params["id"]
        if get_data(unique_id):
            second_user_form(unique_id)
        else:
            st.error("Invalid or expired link.")
    else:
        first_user_form()

def first_user_form():
    st.header("Step 1: Fill in your details, signature, and score")

    user_name = st.text_input("Your Name")
    user_signature = st.text_area("Your Signature (type here)")
    user_score = st.number_input("Your Score", min_value=0, max_value=100, step=1)
    second_user_email = st.text_input("Second User's Email")

    if st.button("Generate Link for Second User"):
        if user_name and user_signature and user_score is not None and second_user_email:
            # Save the initial data
            initial_data = {
                "user_name": user_name,
                "user_signature": user_signature,
                "user_score": user_score,
                "second_user_name": None,
                "second_user_signature": None,
                "second_user_score": None
            }
            link, unique_id = generate_unique_link()
            save_data(unique_id, initial_data)
            
            if send_email(second_user_email, link):
                st.success("Link generated and email sent! The second user will receive an email to complete the form.")
            else:
                st.error("Failed to send email. Please check the email credentials and try again.")
        else:
            st.error("Please fill in all the fields.")

def second_user_form(unique_id):
    st.header("Step 2: Second User Completes the Form")

    user_data = get_data(unique_id)
    if user_data:
        st.write(f"Name of first user: {user_data['user_name']}")
        st.write(f"Signature of first user: {user_data['user_signature']}")
        st.write(f"Score of first user: {user_data['user_score']}")

        second_user_name = st.text_input("Your Name")
        second_user_signature = st.text_area("Your Signature (type here)")
        second_user_score = st.number_input("Your Score", min_value=0, max_value=100, step=1)

        if st.button("Submit"):
            if second_user_name and second_user_signature and second_user_score is not None:
                # Update second user's data
                user_data["second_user_name"] = second_user_name
                user_data["second_user_signature"] = second_user_signature
                user_data["second_user_score"] = second_user_score
                update_data(unique_id, user_data)
                
                st.success("Form completed and submitted successfully!")
                st.json(user_data)
            else:
                st.error("Please fill in all the fields.")
    else:
        st.error("Invalid or expired link.")

# Admin page
def admin():
    st.title("Admin Page")

    admin_user = st.text_input("Username")
    admin_pass = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        signupuser = st.text_input("Create Username")
        signuppass = st.text_input("Create Password", type="password")
        
        sign_up(signupuser, signuppass)
        st.success("User Successfully Added")

    if st.button("Login"):
        if admin_user == "admin" and admin_pass == "password":
            st.success("Logged in as admin")
            data = get_all_data()
            if data:
                df = pd.DataFrame(data, columns=['ID', 'User Name', 'User Signature', 'User Score', 'Second User Name', 'Second User Signature', 'Second User Score'])
                st.dataframe(df)

                # Download as Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                    writer.close()
                st.download_button(label="Download Excel", data=buffer.getvalue(), file_name="responses.xlsx", mime="application/vnd.ms-excel")

                # Download as PDF
                pdf_buffer = io.BytesIO()
                for i, row in df.iterrows():
                    pdf = create_pdf(row.to_dict())
                    pdf_buffer.write(pdf)
                st.download_button(label="Download PDF", data=pdf_buffer.getvalue(), file_name="responses.pdf", mime="application/pdf")

                # Send PDFs to recipients
                if st.button("Send PDFs to Recipients"):
                    for i, row in df.iterrows():
                        user_email = row['User Name']
                        pdf_data = create_pdf(row.to_dict())
                        send_pdf_via_email(user_email, pdf_data, f"form_response_{row['ID']}.pdf")
                    st.success("PDFs sent successfully!")
            else:
                st.warning("No data found.")
        else:
            st.error("Invalid credentials.")

if __name__ == "__main__":
    init_db()
    page = st.sidebar.selectbox(
        "Select a page",
        ["Home", "Admin"]
    )

    if page == "Home":
        home()
    elif page == "Admin":
        admin()
