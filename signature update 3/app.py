import streamlit as st
from streamlit_drawable_canvas import st_canvas
import sqlite3
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid

# Initialize database
def init_db():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
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
            second_user_score INTEGER,
            user_planning_preparation INTEGER,
            user_instructional_process INTEGER,
            user_assessment INTEGER,
            user_professionalism INTEGER,
            user_interpersonal_relationships INTEGER,
            user_classroom_management INTEGER,
            second_user_planning_preparation INTEGER,
            second_user_instructional_process INTEGER,
            second_user_assessment INTEGER,
            second_user_professionalism INTEGER,
            second_user_interpersonal_relationships INTEGER,
            second_user_classroom_management INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Generate unique link
def generate_unique_link():
    unique_id = str(uuid.uuid4())
    link = f"http://localhost:8501/?id={unique_id}"
    return link, unique_id

# Save data to database
def save_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO forms (id, user_name, user_email, user_signature, user_score, second_user_name, second_user_email, second_user_signature, second_user_score,
        user_planning_preparation, user_instructional_process, user_assessment, user_professionalism, user_interpersonal_relationships, user_classroom_management,
        second_user_planning_preparation, second_user_instructional_process, second_user_assessment, second_user_professionalism, second_user_interpersonal_relationships, second_user_classroom_management)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (unique_id, data.get('user_name'), data.get('user_email'), data.get('user_signature'), data.get('user_score'),
          data.get('second_user_name'), data.get('second_user_email'), data.get('second_user_signature'), data.get('second_user_score'),
          data.get('user_planning_preparation'), data.get('user_instructional_process'), data.get('user_assessment'), data.get('user_professionalism'),
          data.get('user_interpersonal_relationships'), data.get('user_classroom_management'),
          data.get('second_user_planning_preparation'), data.get('second_user_instructional_process'), data.get('second_user_assessment'), data.get('second_user_professionalism'),
          data.get('second_user_interpersonal_relationships'), data.get('second_user_classroom_management')))
    conn.commit()
    conn.close()

# Update data in database
def update_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        UPDATE forms SET second_user_name=?, second_user_email=?, second_user_signature=?, second_user_score=?,
        second_user_planning_preparation=?, second_user_instructional_process=?, second_user_assessment=?, second_user_professionalism=?, second_user_interpersonal_relationships=?, second_user_classroom_management=?
        WHERE id=?
    ''', (data.get('second_user_name'), data.get('second_user_email'), data.get('second_user_signature'), data.get('second_user_score'),
          data.get('second_user_planning_preparation'), data.get('second_user_instructional_process'), data.get('second_user_assessment'), data.get('second_user_professionalism'),
          data.get('second_user_interpersonal_relationships'), data.get('second_user_classroom_management'), unique_id))
    conn.commit()
    conn.close()

# Get data from database
def get_data(unique_id):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM forms WHERE id=?', (unique_id,))
    data = c.fetchone()
    conn.close()
    keys = ['id', 'user_name', 'user_email', 'user_signature', 'user_score', 'second_user_name', 'second_user_email',
            'second_user_signature', 'second_user_score', 'user_planning_preparation', 'user_instructional_process', 'user_assessment',
            'user_professionalism', 'user_interpersonal_relationships', 'user_classroom_management',
            'second_user_planning_preparation', 'second_user_instructional_process', 'second_user_assessment', 'second_user_professionalism',
            'second_user_interpersonal_relationships', 'second_user_classroom_management']
    return dict(zip(keys, data))

# Create PDF from form data
def create_pdf(form_data):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Form Response", ln=True, align="C")

    pdf.cell(200, 10, txt=f"First User Name: {form_data['user_name']}", ln=True)
    pdf.cell(200, 10, txt=f"First User Email: {form_data['user_email']}", ln=True)
    pdf.cell(200, 10, txt=f"First User Score: {form_data['user_score']}", ln=True)

    pdf.cell(200, 10, txt=f"Planning and Preparation (User 1): {form_data['user_planning_preparation']}", ln=True)
    pdf.cell(200, 10, txt=f"Instructional Process (User 1): {form_data['user_instructional_process']}", ln=True)
    pdf.cell(200, 10, txt=f"Assessment (User 1): {form_data['user_assessment']}", ln=True)
    pdf.cell(200, 10, txt=f"Professionalism (User 1): {form_data['user_professionalism']}", ln=True)
    pdf.cell(200, 10, txt=f"Interpersonal Relationships (User 1): {form_data['user_interpersonal_relationships']}", ln=True)
    pdf.cell(200, 10, txt=f"Classroom Management (User 1): {form_data['user_classroom_management']}", ln=True)

    pdf.cell(200, 10, txt=f"Second User Name: {form_data['second_user_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Second User Email: {form_data['second_user_email']}", ln=True)
    pdf.cell(200, 10, txt=f"Second User Score: {form_data['second_user_score']}", ln=True)

    pdf.cell(200, 10, txt=f"Planning and Preparation (User 2): {form_data['second_user_planning_preparation']}", ln=True)
    pdf.cell(200, 10, txt=f"Instructional Process (User 2): {form_data['second_user_instructional_process']}", ln=True)
    pdf.cell(200, 10, txt=f"Assessment (User 2): {form_data['second_user_assessment']}", ln=True)
    pdf.cell(200, 10, txt=f"Professionalism (User 2): {form_data['second_user_professionalism']}", ln=True)
    pdf.cell(200, 10, txt=f"Interpersonal Relationships (User 2): {form_data['second_user_interpersonal_relationships']}", ln=True)
    pdf.cell(200, 10, txt=f"Classroom Management (User 2): {form_data['second_user_classroom_management']}", ln=True)

    return pdf.output(dest='S').encode('latin1')

# Send email with PDF attachment
def send_email(to_email, pdf_data, filename):
    try:
        msg = MIMEMultipart()
        msg['From'] = 'shsmodernhill@shb.sch.id'
        msg['To'] = to_email
        msg['Subject'] = 'Form Response PDF'

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('shsmodernhill@shb.sch.id', 'jvvmdgxgdyqflcrf')
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Form for the first user
def first_user_form():
    st.header("Step 1: Fill in your details, signature, and score")

    user_name = st.text_input("Your Name")
    user_email = st.text_input("Your Email")
    user_score = st.slider("Your Score", min_value=0, max_value=100, step=1)
    second_user_email = st.text_input("Second User's Email")

    # Add rubric questions as sliders for the first user
    st.subheader("Planning and Preparation")
    user_planning_preparation = st.slider("Rate Planning and Preparation", min_value=0, max_value=5, step=1)

    st.subheader("Instructional Process")
    user_instructional_process = st.slider("Rate Instructional Process", min_value=0, max_value=5, step=1)

    st.subheader("Assessment")
    user_assessment = st.slider("Rate Assessment", min_value=0, max_value=5, step=1)

    st.subheader("Professionalism")
    user_professionalism = st.slider("Rate Professionalism", min_value=0, max_value=5, step=1)

    st.subheader("Interpersonal Relationships")
    user_interpersonal_relationships = st.slider("Rate Interpersonal Relationships", min_value=0, max_value=5, step=1)

    st.subheader("Classroom Management")
    user_classroom_management = st.slider("Rate Classroom Management", min_value=0, max_value=5, step=1)

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
        key="user_signature",
    )

    if st.button("Submit"):
        if user_name and user_email and second_user_email and user_signature_canvas.image_data is not None:
            user_signature_image = Image.fromarray(user_signature_canvas.image_data.astype('uint8'), 'RGBA')
            user_signature_bytes = BytesIO()
            user_signature_image.save(user_signature_bytes, format='PNG')
            user_signature_bytes = user_signature_bytes.getvalue()

            data = {
                "user_name": user_name,
                "user_email": user_email,
                "user_signature": user_signature_bytes,
                "user_score": user_score,
                "second_user_email": second_user_email,
                "user_planning_preparation": user_planning_preparation,
                "user_instructional_process": user_instructional_process,
                "user_assessment": user_assessment,
                "user_professionalism": user_professionalism,
                "user_interpersonal_relationships": user_interpersonal_relationships,
                "user_classroom_management": user_classroom_management
            }

            link, unique_id = generate_unique_link()
            save_data(unique_id, data)
            st.success("Form submitted successfully.")
            st.markdown(f"[Link for the second user]({link})")
        else:
            st.error("Please fill all the details and provide your signature.")

# Form for the second user
def second_user_form(unique_id):
    data = get_data(unique_id)
    st.header("Step 2: Fill in your details, signature, and score")

    second_user_name = st.text_input("Your Name")
    second_user_email = data['second_user_email']
    st.text(f"Second User Email: {second_user_email}")
    second_user_score = st.slider("Your Score", min_value=0, max_value=100, step=1)

    # Add rubric questions as sliders for the second user
    st.subheader("Planning and Preparation")
    second_user_planning_preparation = st.slider("Rate Planning and Preparation", min_value=0, max_value=5, step=1)

    st.subheader("Instructional Process")
    second_user_instructional_process = st.slider("Rate Instructional Process", min_value=0, max_value=5, step=1)

    st.subheader("Assessment")
    second_user_assessment = st.slider("Rate Assessment", min_value=0, max_value=5, step=1)

    st.subheader("Professionalism")
    second_user_professionalism = st.slider("Rate Professionalism", min_value=0, max_value=5, step=1)

    st.subheader("Interpersonal Relationships")
    second_user_interpersonal_relationships = st.slider("Rate Interpersonal Relationships", min_value=0, max_value=5, step=1)

    st.subheader("Classroom Management")
    second_user_classroom_management = st.slider("Rate Classroom Management", min_value=0, max_value=5, step=1)

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

    if st.button("Submit"):
        if second_user_name and second_user_signature_canvas.image_data is not None and second_user_score is not None:
            second_user_signature_image = Image.fromarray(second_user_signature_canvas.image_data.astype('uint8'), 'RGBA')
            second_user_signature_bytes = BytesIO()
            second_user_signature_image.save(second_user_signature_bytes, format='PNG')
            second_user_signature_bytes = second_user_signature_bytes.getvalue()

            data.update({
                "second_user_name": second_user_name,
                "second_user_email": second_user_email,
                "second_user_signature": second_user_signature_bytes,
                "second_user_score": second_user_score,
                "second_user_planning_preparation": second_user_planning_preparation,
                "second_user_instructional_process": second_user_instructional_process,
                "second_user_assessment": second_user_assessment,
                "second_user_professionalism": second_user_professionalism,
                "second_user_interpersonal_relationships": second_user_interpersonal_relationships,
                "second_user_classroom_management": second_user_classroom_management
            })

            update_data(unique_id, data)

            pdf_data = create_pdf(data)
            if send_email(data['user_email'], pdf_data, f"{unique_id}.pdf"):
                st.success("Form data and PDF sent successfully.")
            else:
                st.error("Failed to send email.")
        else:
            st.error("Please fill all the details and provide your signature.")

# Main application logic
def main():
    st.title("Two-Step Form Submission with Signature and Rubric Questions")

    init_db()

    query_params = st.experimental_get_query_params()
    unique_id = query_params.get("id", [None])[0]

    if unique_id:
        second_user_form(unique_id)
    else:
        first_user_form()

if __name__ == "__main__":
    main()
