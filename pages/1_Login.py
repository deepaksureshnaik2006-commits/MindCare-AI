import streamlit as st
import json
import os

st.set_page_config(page_title="Login • MindCare AI", layout="centered")

USER_DB = "users.json"

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

# Load / Save users
def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)

st.markdown("<h1 style='text-align:center;'>🌱 MindCare AI</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Sign Up", "🗑️ Delete Account"])

# ========== LOGIN ==========
with tab1:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()

        if email in users and users[email]["password"] == password:
            st.session_state["user"] = email
            st.success("Logged in!")
            st.switch_page("pages/2_Chat.py")
        else:
            st.error("Invalid email or password")

    if st.button("Continue as Guest"):
        st.session_state["user"] = "guest"
        st.success("Proceeding as guest...")
        st.switch_page("pages/2_Chat.py")

# ========== SIGNUP ==========
with tab2:
    st.subheader("Create Account")

    new_email = st.text_input("New Email")
    new_password = st.text_input("New Password", type="password")

    if st.button("Create Account"):
        users = load_users()

        if new_email in users:
            st.error("This email already exists.")
        else:
            users[new_email] = {"password": new_password}
            save_users(users)
            st.success("Account created! Please login.")

# ========== DELETE ACCOUNT ==========
with tab3:
    st.subheader("Delete Account")
    del_email = st.text_input("Enter Email")
    del_pass = st.text_input("Enter Password", type="password")

    if st.button("Delete Account"):
        users = load_users()

        if del_email in users and users[del_email]["password"] == del_pass:
            users.pop(del_email)
            save_users(users)
            st.success("Account deleted permanently.")
        else:
            st.error("Invalid email or password")
