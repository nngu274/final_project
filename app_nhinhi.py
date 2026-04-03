import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid

st.set_page_config(page_title="Whimsical Sweets Operations Portal", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None


users_path = Path("users.json")
products_path = Path("products.json")
sales_path = Path("sales.json")

if users_path.exists():
    with users_path.open("r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = []

if products_path.exists():
    with products_path.open("r", encoding="utf-8") as f:
        products = json.load(f)
else:
    products = []

if sales_path.exists():
    with sales_path.open("r", encoding="utf-8") as f:
        sales_log = json.load(f)
else:
    sales_log = []

def save_products():
    with products_path.open("w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)

def save_users():
    with users_path.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def save_sales():
    with sales_path.open("w", encoding="utf-8") as f:
        json.dump(sales_log, f, indent=2)

def find_product_by_name(name):
    for product in products:
        if product["name"] == name:
            return product
    return None

if not st.session_state["logged_in"]:
    st.title("Whimsical Sweets Operations Portal")

    tab1, tab2 = st.tabs(["Log In", "Create Account"])

    with tab1:
        email_input = st.text_input("Email")
        password_input = st.text_input("Password", type="password")

        if st.button("Log In", use_container_width=True):
            found_user = None
            for user in users:
                if (
                    user["email"].strip().lower() == email_input.strip().lower()
                    and user["password"] == password_input
                ):
                    found_user = user
                    break

            if found_user:
                st.session_state["logged_in"] = True
                st.session_state["user"] = found_user
                st.session_state["role"] = found_user["role"]
                st.success(f"Welcome, {found_user['email']}!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["Shop Owner", "Employee"])

        if st.button("Create Account", use_container_width=True):
            users.append({
                "id": str(uuid.uuid4()),
                "email": new_email,
                "password": new_password,
                "role": new_role
            })
            save_users()
            st.success("Account created successfully.")
            st.rerun()


else:
    st.title("Whimsical Sweets Operations Portal")
    st.write(f"Logged in as: **{st.session_state['user']['email']}**")
    st.write(f"Role: **{st.session_state['role']}**")

    if st.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.rerun()