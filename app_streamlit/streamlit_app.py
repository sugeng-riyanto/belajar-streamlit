import streamlit as st
import requests

# URL of the Flask backend (ensure the port matches the one in flask_app.py)
FLASK_API_URL = "http://127.0.0.1:5001/api/users"

# Function to get all users
def get_users():
    response = requests.get(FLASK_API_URL)
    return response.json()

# Function to add a new user
def add_user(name, age, email):
    user = {"id": len(get_users()) + 1, "name": name, "age": age, "email": email}
    response = requests.post(FLASK_API_URL, json=user)
    return response.json()

# Function to update a user
def update_user(user_id, name, age, email):
    user = {"name": name, "age": age, "email": email}
    response = requests.put(f"{FLASK_API_URL}/{user_id}", json=user)
    return response.json()

# Function to delete a user
def delete_user(user_id):
    response = requests.delete(f"{FLASK_API_URL}/{user_id}")
    return response.status_code

# Streamlit UI
st.title("CRUD App with Streamlit, Flask, HTML, and CSS")

menu = ["Create", "Read", "Update", "Delete"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Create":
    st.subheader("Add a New User")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    email = st.text_input("Email")
    if st.button("Add User"):
        add_user(name, age, email)
        st.success(f"User '{name}' added successfully!")

elif choice == "Read":
    st.subheader("View All Users")
    users = get_users()
    for user in users:
        st.write(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}, Email: {user['email']}")

elif choice == "Update":
    st.subheader("Update User Information")
    user_id = st.number_input("User ID", min_value=1)
    name = st.text_input("New Name")
    age = st.number_input("New Age", min_value=0, max_value=120)
    email = st.text_input("New Email")
    if st.button("Update User"):
        update_user(user_id, name, age, email)
        st.success(f"User ID '{user_id}' updated successfully!")

elif choice == "Delete":
    st.subheader("Delete a User")
    user_id = st.number_input("User ID to Delete", min_value=1)
    if st.button("Delete User"):
        delete_user(user_id)
        st.success(f"User ID '{user_id}' deleted successfully!")

# Custom HTML and CSS
st.markdown("""
    <style>
    .stButton>button {
        color: white;
        background-color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)
