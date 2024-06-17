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

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id TEXT PRIMARY KEY,
            user_name TEXT,
            user_email TEXT,
            user_signature BLOB,
            planning_preparation INTEGER,
            instructional_process INTEGER,
            assessment INTEGER,
            professionalism INTEGER,
            interpersonal_relationships INTEGER,
            classroom_management INTEGER,
            second_user_name TEXT,
            second_user_email TEXT,
            second_user_signature BLOB,
            second_planning_preparation INTEGER,
            second_instructional_process INTEGER,
            second_assessment INTEGER,
            second_professionalism INTEGER,
            second_interpersonal_relationships INTEGER,
            second_classroom_management INTEGER
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    c.execute('''
        INSERT OR IGNORE INTO admins (username, password)
        VALUES (?, ?)
    ''', ('admin', 'password'))

    conn.commit()
    conn.close()

def calculate_total_score(scores):
    weights = {
        "planning_preparation": 20,
        "instructional_process": 25,
        "assessment": 20,
        "professionalism": 10,
        "interpersonal_relationships": 10,
        "classroom_management": 15
    }

    total_score = sum(scores[category] * weights[category] / 100 for category in weights)
    return total_score

def generate_unique_link():
    unique_id = str(uuid.uuid4())
    return f"http://localhost:8501/?id={unique_id}", unique_id

def save_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO forms (id, user_name, user_email, user_signature, planning_preparation, instructional_process, assessment, professionalism, interpersonal_relationships, classroom_management, second_user_name, second_user_email, second_user_signature, second_planning_preparation, second_instructional_process, second_assessment, second_professionalism, second_interpersonal_relationships, second_classroom_management)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (unique_id, data.get('user_name'), data.get('user_email'), data.get('user_signature'),
          data.get('planning_preparation'), data.get('instructional_process'), data.get('assessment'),
          data.get('professionalism'), data.get('interpersonal_relationships'), data.get('classroom_management'),
          data.get('second_user_name'), data.get('second_user_email'), data.get('second_user_signature'),
          data.get('second_planning_preparation'), data.get('second_instructional_process'), data.get('second_assessment'),
          data.get('second_professionalism'), data.get('second_interpersonal_relationships'), data.get('second_classroom_management')))
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
            'user_email': data[2],
            'user_signature': data[3],
            'planning_preparation': data[4],
            'instructional_process': data[5],
            'assessment': data[6],
            'professionalism': data[7],
            'interpersonal_relationships': data[8],
            'classroom_management': data[9],
            'second_user_name': data[10],
            'second_user_email': data[11],
            'second_user_signature': data[12],
            'second_planning_preparation': data[13],
            'second_instructional_process': data[14],
            'second_assessment': data[15],
            'second_professionalism': data[16],
            'second_interpersonal_relationships': data[17],
            'second_classroom_management': data[18]
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
        SET second_user_name = ?, second_user_email = ?, second_user_signature = ?, second_planning_preparation = ?, second_instructional_process = ?, second_assessment = ?, second_professionalism = ?, second_interpersonal_relationships = ?, second_classroom_management = ?
        WHERE id = ?
    ''', (data.get('second_user_name'), data.get('second_user_email'), data.get('second_user_signature'), data.get('second_planning_preparation'), data.get('second_instructional_process'), data.get('second_assessment'), data.get('second_professionalism'), data.get('second_interpersonal_relationships'), data.get('second_classroom_management'), unique_id))
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

def sign_up(username, password):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def home():
    st.header("Step 1: Enter Details, Signature, and Score")

    user_name = st.text_input("Your Name", key="user_name")
    user_email = st.text_input("Your Email", key="user_email")

    st.write("Draw your signature below:")

    signature_canvas = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent background
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        update_streamlit=True,
        height=150,
        drawing_mode="freedraw",
        key="canvas",
    )

    st.write("Score for each area:")

    planning_preparation = st.number_input("Planning and Preparation", min_value=0, max_value=100, step=1, key="planning_preparation")
    instructional_process = st.number_input("Instructional Process", min_value=0, max_value=100, step=1, key="instructional_process")
    assessment = st.number_input("Assessment", min_value=0, max_value=100, step=1, key="assessment")
    professionalism = st.number_input("Professionalism", min_value=0, max_value=100, step=1, key="professionalism")
    interpersonal_relationships = st.number_input("Interpersonal Relationships", min_value=0, max_value=100, step=1, key="interpersonal_relationships")
    classroom_management = st.number_input("Classroom Management", min_value=0, max_value=100, step=1, key="classroom_management")

    total_score = calculate_total_score({
        "planning_preparation": planning_preparation,
        "instructional_process": instructional_process,
        "assessment": assessment,
        "professionalism": professionalism,
        "interpersonal_relationships": interpersonal_relationships,
        "classroom_management": classroom_management
    })

    second_user_email = st.text_input("Second User's Email", key="second_user_email")

    if st.button("Submit and Send Link"):
        if not user_name or not user_email or not second_user_email:
            st.warning("Please fill in all fields.")
        elif signature_canvas.image_data is None:
            st.warning("Please draw your signature.")
        else:
            link, unique_id = generate_unique_link()
            img = Image.fromarray(signature_canvas.image_data.astype("uint8"), "RGBA")
            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG")
            img_bytes = img_buffer.getvalue()

            data = {
                'user_name': user_name,
                'user_email': user_email,
                'user_signature': img_bytes,
                'planning_preparation': planning_preparation,
                'instructional_process': instructional_process,
                'assessment': assessment,
                'professionalism': professionalism,
                'interpersonal_relationships': interpersonal_relationships,
                'classroom_management': classroom_management,
                'second_user_email': second_user_email
            }
            save_data(unique_id, data)
            if send_email(second_user_email, link):
                st.success("Link sent successfully!")
                st.write(f"Share this link with the second user: {link}")
            else:
                st.error("Failed to send email. Please try again.")

def second_user_form(unique_id):
    st.header("Step 2: Second User's Details, Signature, and Score")

    data = get_data(unique_id)

    if not data:
        st.error("Invalid or expired link.")
        return

    st.write(f"First User: {data['user_name']}")
    st.write(f"First User Scores: Planning and Preparation - {data['planning_preparation']}, Instructional Process - {data['instructional_process']}, Assessment - {data['assessment']}, Professionalism - {data['professionalism']}, Interpersonal Relationships - {data['interpersonal_relationships']}, Classroom Management - {data['classroom_management']}")

    second_user_name = st.text_input("Your Name", key="second_user_name")
    second_user_email = st.text_input("Your Email", key="second_user_email")

    st.write("Draw your signature below:")

    signature_canvas = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent background
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        update_streamlit=True,
        height=150,
        drawing_mode="freedraw",
        key="second_canvas",
    )

    st.write("Score for each area:")

    second_planning_preparation = st.number_input("Planning and Preparation", min_value=0, max_value=100, step=1, key="second_planning_preparation")
    second_instructional_process = st.number_input("Instructional Process", min_value=0, max_value=100, step=1, key="second_instructional_process")
    second_assessment = st.number_input("Assessment", min_value=0, max_value=100, step=1, key="second_assessment")
    second_professionalism = st.number_input("Professionalism", min_value=0, max_value=100, step=1, key="second_professionalism")
    second_interpersonal_relationships = st.number_input("Interpersonal Relationships", min_value=0, max_value=100, step=1, key="second_interpersonal_relationships")
    second_classroom_management = st.number_input("Classroom Management", min_value=0, max_value=100, step=1, key="second_classroom_management")

    total_score = calculate_total_score({
        "planning_preparation": second_planning_preparation,
        "instructional_process": second_instructional_process,
        "assessment": second_assessment,
        "professionalism": second_professionalism,
        "interpersonal_relationships": second_interpersonal_relationships,
        "classroom_management": second_classroom_management
    })

    if st.button("Submit"):
        if not second_user_name or not second_user_email:
            st.warning("Please fill in all fields.")
        elif signature_canvas.image_data is None:
            st.warning("Please draw your signature.")
        else:
            img = Image.fromarray(signature_canvas.image_data.astype("uint8"), "RGBA")
            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG")
            img_bytes = img_buffer.getvalue()

            update_data(unique_id, {
                'second_user_name': second_user_name,
                'second_user_email': second_user_email,
                'second_user_signature': img_bytes,
                'second_planning_preparation': second_planning_preparation,
                'second_instructional_process': second_instructional_process,
                'second_assessment': second_assessment,
                'second_professionalism': second_professionalism,
                'second_interpersonal_relationships': second_interpersonal_relationships,
                'second_classroom_management': second_classroom_management
            })

            form_data = get_data(unique_id)
            pdf_data = create_pdf(form_data)
            if send_pdf_via_email(form_data['user_email'], pdf_data, "form_response.pdf") and send_pdf_via_email(second_user_email, pdf_data, "form_response.pdf"):
                st.success("Form submitted and emails sent successfully!")
            else:
                st.error("Failed to send email. Please try again.")

# Admin page
def admin_page():
    st.title("Admin Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "password":
            st.success("Logged in successfully.")
            show_all_data()
        else:
            st.error("Invalid username or password.")

def show_all_data():
    st.header("All Form Data")
    data = get_all_data()
    df = pd.DataFrame(data, columns=['ID', 'User Name', 'User Email', 'User Signature', 'Planning and Preparation', 'Instructional Process', 'Assessment', 'Professionalism', 'Interpersonal Relationships', 'Classroom Management', 'Second User Name', 'Second User Email', 'Second User Signature', 'Second Planning and Preparation', 'Second Instructional Process', 'Second Assessment', 'Second Professionalism', 'Second Interpersonal Relationships', 'Second Classroom Management'])
    st.dataframe(df)

def main():
    init_db()

    menu = ["Home", "Admin"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        home()
    elif choice == "Admin":
        admin_page()

if __name__ == '__main__':
    main()
