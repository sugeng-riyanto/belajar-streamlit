import streamlit as st
import sqlite3
from datetime import datetime

# Section headers and percentages
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
    "Planning and Preparation": [
        "Prepares and submits schemes of work related to the scope and sequence of the curriculum",
        "Prepares lesson plans",
        "Prepares lesson plans that are well laid out and sequenced",
        "Writes objectives that are clear",
        "Writes objectives that are level appropriate",
        "Selects objectives that are achievable",
        "Prepares content that is a good match for the objectives",
        "Demonstrates sound judgment in decision making",
        "Plans activities that are well differentiated",
        "Prepares instruction with opportunities for individual work",
        "Prepares instruction with opportunities for group work",
        "Prepares materials that are usable in the setting",
        "Prepares instructional materials that are adequate",
        "Includes timing as an integral part of the planning",
        "Is well organized for lesson presentation",
        "Prepares assessment exercises to monitor students' learning"
    ],
    "Instructional Process": [
        "Welcomes/settles the class appropriately",
        "Makes objectives explicit to students at the start of the lessons",
        "Engages students in activities that are appropriate",
        "Engages students in activities that are meaningful",
        "Engages students in activities that encourage them to think",
        "Demonstrates an awareness of students' levels of performance",
        "Teaches in harmony with objectives",
        "Uses a variety of teaching strategies to enhance learning",
        "Demonstrates a good grasp of the subject matter",
        "Presents correct information",
        "Arouses and maintains students' interest",
        "Uses appropriate instructional materials in the teaching/learning environment",
        "Uses appropriate questioning techniques",
        "Gives students opportunities to respond to questions",
        "Ensures that all students participate in instructional activities",
        "Makes effective use of a variety of organizational structures (whole class, small groups, pairs, one-on-one)",
        "Guides students to develop concepts/master skills",
        "Presents instruction in a logical and coherent manner",
        "Ends lessons appropriately",
        "Achieves instructional objectives"
    ],
    "Assessment": [
        "Communicates clear criteria/standards for assessment to students",
        "Uses appropriate assessment activities to monitor student performance",
        "Designs assessment exercises at the appropriate level(s) of difficulty",
        "Regularly assesses during lesson to ascertain students' understanding",
        "Provides corrective feedback during the course of the lesson",
        "Maintains accurate records of students' performance",
        "Frequently monitors each student's progress",
        "Provides timely feedback to students of their performance",
        "Provides timely feedback to parents on students' performance",
        "Takes appropriate action based on results of assessments"
    ],
    "Professionalism": [
        "Expresses himself/herself clearly and is easily understood",
        "Excellent attendance",
        "Arrives for work on time, arrives for lessons on time",
        "Reports for work regularly",
        "Ensures the safety of all students",
        "Demonstrates maturity in dealing with students",
        "Demonstrates sound judgment in decision-making",
        "Years of service",
        "Participates in professional development and seeks opportunities for his/her professional development",
        "Demonstrates leadership skills in the performance of duties",
        "Contributes to the life of the school including co-curricular activities",
        "Submits required information (reports, data, etc) on time",
        "Adheres to the code of ethics"
    ],
    "Interpersonal Relationships": [
        "Encourages students to respect the worth and dignity of others",
        "Offers advice to others (principal, colleagues, students, parents)",
        "Accepts advice from others (principals, colleagues, students, parents)",
        "Is cooperative and works well with staff members",
        "Demonstrates sensitivity to opinions, attitudes, and feelings of others",
        "Communicates effectively with students",
        "Communicates effectively with colleagues",
        "Communicates effectively with principals",
        "Communicates effectively with support/ancillary staff",
        "Communicates effectively with parents",
        "Maintains a good rapport with students",
        "Maintains a good rapport with colleagues",
        "Maintains a good rapport with principals",
        "Maintains a good rapport with support/ancillary staff",
        "Maintains a good rapport with parents"
    ],
    "Classroom Management": [
        "Demonstrates an awareness of what is happening in the classroom",
        "Creates an atmosphere conducive to learning",
        "Deals effectively with students' behavior",
        "Is fair in dealing with students",
        "Manages time effectively",
        "Manages and utilizes learning resources effectively",
        "Manages effectively classroom-related activities, assignments, projects, field trips etc.",
        "Ensures that students observe the rules for classroom activities and students' behavior",
        "Demonstrates effective transition from one activity to another during instruction",
        "Takes a class register",
        "Keeps accurate and relevant students' records"
    ]
}

# Overall interpretation
def interpret_score(score):
    if score >= 90:
        return "EXCELLENT"
    elif score >= 80:
        return "VERY GOOD"
    elif score >= 70:
        return "GOOD"
    elif score >= 60:
        return "SATISFACTORY"
    else:
        return "UNSATISFACTORY"

# Create a connection to the SQLite database
conn = sqlite3.connect('assessment.db')
c = conn.cursor()

# Create the assessments table if it does not exist
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

# Streamlit form
st.title("Teachers' Performance Assessment")

teacher_name = st.text_input("Name of Teacher:")
subject = st.text_input("Subject(s):")
observation_date = st.date_input("Date for Classroom Observation:")
observation_time = st.time_input("Time for Classroom Observation:")

# Store the section scores in session state to update dynamically
if 'section_scores' not in st.session_state:
    st.session_state.section_scores = {section: 0 for section in sections}

# Function to calculate the total score dynamically
def calculate_total_score():
    total = 0
    for section, weight in sections.items():
        section_total = sum(st.session_state.get(f"{section}_{item}", 0) for item in subsections[section])
        weighted_section_score = (section_total / (len(subsections[section]) * 4)) * weight
        st.session_state.section_scores[section] = weighted_section_score
        total += weighted_section_score
    st.session_state.total_score = total

# Initialize the total score in session state
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0

# Streamlit form with dynamic score calculation
with st.form(key='assessment_form'):
    for section, weight in sections.items():
        st.header(f"{section} ({weight}%)")
        total_section_score = 0
        max_section_score = len(subsections[section]) * 4

        for item in subsections[section]:
            score = st.slider(item, 0, 4, 3, key=f"{section}_{item}")
            total_section_score += score

        weighted_section_score = (total_section_score / max_section_score) * weight
        st.session_state.section_scores[section] = weighted_section_score

    calculate_total_score()
    st.subheader("Overall Score")
    st.write(f"Total Score: {st.session_state.total_score:.2f} / 100")
    st.write(f"Overall Rating: {interpret_score(st.session_state.total_score)}")

    # Submit button
    submitted = st.form_submit_button(label='Check')
    sent=st.form.form_submit_button(label='Send')

if sent:
    st.success("Assessment sent successfully!")
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

    # Insert the data into the SQLite database
    c.execute('''
        INSERT INTO assessments (teacher_name, subject, observation_date, observation_time, total_score, overall_rating)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (teacher_name, subject, str(observation_date), str(observation_time), st.session_state.total_score, interpret_score(st.session_state.total_score)))
    conn.commit()

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


# Close the database connection
conn.close()
