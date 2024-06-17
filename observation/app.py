import streamlit as st
import sqlite3
import pandas as pd
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader
from fpdf import FPDF
from datetime import datetime

# Section headers and percentages for assessment
sections = {
    "Planning and Preparation": 20,
    "Instructional Process": 25,
    "Assessment": 20,
    "Professionalism": 10,
    "Interpersonal Relationships": 10,
    "Classroom Management": 15
}

# Subsections for each section
subsections = {
    # Subsections as provided in the second script
}

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    # Form data table
    c.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id TEXT PRIMARY KEY,
            user_name TEXT,
            user_email TEXT,
            user_signature BLOB,
            user_score INTEGER,
            second_user_name TEXT,
            second_user_email TEXT,
            second_user_signature BLOB,
            second_user_score INTEGER
        )
    ''')

    # Admins table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Assessments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY,
            teacher_name TEXT,
            subject TEXT,
            observation_date TEXT,
            observation_time TEXT,
            total_score REAL,
            overall_rating TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Email sending function
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

# PDF generation and sending functions
def generate_pdf(signature_image, sender_name):
    pdf_buffer = BytesIO()
    c = pdf_canvas.Canvas(pdf_buffer, pagesize=letter)
    c.drawString(100, 700, f"Signed by: {sender_name}")
    img_temp = BytesIO()
    signature_image.save(img_temp, format='PNG')
    img_temp.seek(0)
    c.drawImage(ImageReader(img_temp), 100, 100, width=300, height=100)
    c.save()
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_bytes

def create_pdf(data):
    pdf_buffer = BytesIO()
    c = pdf_canvas.Canvas(pdf_buffer, pagesize=letter)
    c.drawString(100, 750, "Form Response")
    y = 700
    for key, value in data.items():
        if key.endswith('signature'):
            img_temp = BytesIO(value)
            img_temp.seek(0)
            c.drawImage(ImageReader(img_temp), 100, y-100, width=300, height=100)
            y -= 150
        else:
            c.drawString(100, y, f"{key}: {value}")
            y -= 50
    c.save()
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_bytes

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
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(pdf_data)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
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

# Function to calculate the total score dynamically
def calculate_total_score():
    total = 0
    for section, weight in sections.items():
        section_total = sum(st.session_state.get(f"{section}_{item}", 0) for item in subsections[section])
        weighted_section_score = (section_total / (len(subsections[section]) * 4)) * weight
        st.session_state.section_scores[section] = weighted_section_score
        total += weighted_section_score
    st.session_state.total_score = total

def first_user_form():
    st.header("Step 1: Fill in your details, signature, and score")
    user_name = st.text_input("Your Name")
    user_email = st.text_input("Your Email")
    user_score = st.number_input("Your Score", min_value=0, max_value=100, step=1)
    second_user_email = st.text_input("Second User's Email")
    st.write("Draw your signature below:")
    user_signature_canvas = st_canvas(
        fill_color="rgb(255, 255, 255)",
        stroke_width=2,
        stroke_color="rgb(0, 0, 0)",
        background_color="rgb(240, 240, 240)",
        update_streamlit=True,
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="first_user_signature",
    )
    if st.button("Generate Link for Second User"):
        if user_name and user_email and user_signature_canvas.image_data is not None and user_score is not None and second_user_email:
            user_signature_image = Image.fromarray(user_signature_canvas.image_data.astype('uint8'), 'RGBA')
            user_signature_bytes = BytesIO()
            user_signature_image.save(user_signature_bytes, format='PNG')
            user_signature_bytes = user_signature_bytes.getvalue()
            initial_data = {
                "user_name": user_name,
                "user_email": user_email,
                "user_signature": user_signature_bytes,
                "user_score": user_score,
                "second_user_name": None,
                "second_user_email": second_user_email,
                "second_user_signature": None,
                "second_user_score": None
            }
            unique_id = str(uuid.uuid4())
            link = f"http://localhost:8501/?id={unique_id}"
            save_data(unique_id, initial_data)
            st.success(f"Link generated: {link}")
            if send_email(second_user_email, link):
                st.success("Email sent to the second user successfully!")
            else:
                st.error("Failed to send email to the second user.")
        else:
            st.error("Please fill in all the details and draw your signature.")

def save_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO forms (id, user_name, user_email, user_signature, user_score, second_user_name, second_user_email, second_user_signature, second_user_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (unique_id, data['user_name'], data['user_email'], data['user_signature'], data['user_score'], data['second_user_name'], data['second_user_email'], data['second_user_signature'], data['second_user_score']))
    conn.commit()
    conn.close()

def update_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        UPDATE forms
        SET second_user_name = ?, second_user_email = ?, second_user_signature = ?, second_user_score = ?
        WHERE id = ?
    ''', (data['second_user_name'], data['second_user_email'], data['second_user_signature'], data['second_user_score'], unique_id))
    conn.commit()
    conn.close()

def get_data(unique_id):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM forms WHERE id = ?
    ''', (unique_id,))
    row = c.fetchone()
    conn.close()
    if row:
        data = {
            "user_name": row[1],
            "user_email": row[2],
            "user_signature": row[3],
            "user_score": row[4],
            "second_user_name": row[5],
            "second_user_email": row[6],
            "second_user_signature": row[7],
            "second_user_score": row[8]
        }
        return data
    return None

def second_user_form(unique_id):
    st.header("Step 2: Complete your details, signature, and score")
    second_user_name = st.text_input("Your Name")
    second_user_email = st.text_input("Your Email")
    second_user_score = st.number_input("Your Score", min_value=0, max_value=100, step=1)
    st.write("Draw your signature below:")
    second_user_signature_canvas = st_canvas(
        fill_color="rgb(255, 255, 255)",
        stroke_width=2,
        stroke_color="rgb(0, 0, 0)",
        background_color="rgb(240, 240, 240)",
        update_streamlit=True,
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="second_user_signature",
    )
    if st.button("Complete Form"):
        if second_user_name and second_user_email and second_user_signature_canvas.image_data is not None and second_user_score is not None:
            second_user_signature_image = Image.fromarray(second_user_signature_canvas.image_data.astype('uint8'), 'RGBA')
            second_user_signature_bytes = BytesIO()
            second_user_signature_image.save(second_user_signature_bytes, format='PNG')
            second_user_signature_bytes = second_user_signature_bytes.getvalue()
            update_data(unique_id, {
                "second_user_name": second_user_name,
                "second_user_email": second_user_email,
                "second_user_signature": second_user_signature_bytes,
                "second_user_score": second_user_score
            })
            final_data = get_data(unique_id)
            st.success("Form completed successfully!")
            st.write(final_data)
            if final_data:
                pdf_bytes = create_pdf(final_data)
                if send_pdf_via_email(final_data['user_email'], pdf_bytes, f"form_{unique_id}.pdf"):
                    st.success("PDF sent to the first user successfully!")
                else:
                    st.error("Failed to send PDF to the first user.")
        else:
            st.error("Please fill in all the details and draw your signature.")

def assessment_form():
    st.title("Teachers' Performance Assessment")
    teacher_name = st.text_input("Name of Teacher:")
    subject = st.text_input("Subject(s):")
    observation_date = st.date_input("Date for Classroom Observation:")
    observation_time = st.time_input("Time for Classroom Observation:")
    if 'section_scores' not in st.session_state:
        st.session_state.section_scores = {section: 0 for section in sections}
    if 'total_score' not in st.session_state:
        st.session_state.total_score = 0
    with st.form(key='assessment_form'):
        for section, weight in sections.items():
            st.header(f"{section} ({weight}%)")
            total_section_score = 0
            max_section_score = len(subsections[section]) * 4
            for item in subsections[section]:
                score = st.slider(item, 0, 4, 0, key=f"{section}_{item}")
                total_section_score += score
            weighted_section_score = (total_section_score / max_section_score) * weight
            st.session_state.section_scores[section] = weighted_section_score
        calculate_total_score()
        st.subheader("Overall Score")
        st.write(f"Total Score: {st.session_state.total_score:.2f} / 100")
        st.write(f"Overall Rating: {interpret_score(st.session_state.total_score)}")
        submitted = st.form_submit_button(label='Submit')
    if submitted:
        st.success("Assessment submitted successfully!")
        st.write(f"Teacher Name: {teacher_name}")
        st.write(f"Subject(s): {subject}")
        st.write(f"Date for Classroom Observation: {observation_date}")
        st.write(f"Time for Classroom Observation: {observation_time}")
        st.write("### Section Scores")
        for section, score in st.session_state.section_scores.items():
            st.write(f"{section}: {score:.2f}")
        st.write("### Overall Score")
        st.write(f"Total Score: {st.session_state.total_score:.2f} / 100")
        st.write(f"Overall Rating: {interpret_score(st.session_state.total_score)}")
        conn = sqlite3.connect('form_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO assessments (teacher_name, subject, observation_date, observation_time, total_score, overall_rating)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (teacher_name, subject, str(observation_date), str(observation_time), st.session_state.total_score, interpret_score(st.session_state.total_score)))
        conn.commit()
        conn.close()

# Streamlit application with navigation
init_db()

st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Choose a form", ("User Signature Form", "Second User Form", "Teacher Performance Assessment"))

if option == "User Signature Form":
    first_user_form()
elif option == "Second User Form":
    unique_id = st.sidebar.text_input("Enter the unique ID")
    if unique_id:
        second_user_form(unique_id)
elif option == "Teacher Performance Assessment":
    assessment_form()
