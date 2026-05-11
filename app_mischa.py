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

def delete_product(delete_name):
    products[:] = [p for p in products if p["name"] != delete_name]
    with products_path.open("w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)


def update_product(selected_name, new_price, restock_amount):
    for product in products:
        if product["name"] == selected_name:
            product["price"] = new_price
            product["stock"] += restock_amount
            if product["stock"] > 5:
                product["low_stock_flag"] = False
            with products_path.open("w", encoding="utf-8") as f:
                json.dump(products, f, indent=2)
            return True
    return False


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
            with users_path.open("w", encoding="utf-8") as f:
                json.dump(users, f, indent=2)
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
if st.session_state["role"] == "Shop Owner":
    tab1, tab2, tab3, tab4 = st.tabs([
            "View Catalog",
            "Add Product",
            "Update / Restock",
            "Delete Product"
        ])

    with tab1:
            st.subheader("Current Shelf Catalog")
            if products:
                st.dataframe(products, use_container_width=True)
            else:
                st.info("No products in the system yet.")

    with tab2:
            st.subheader("Add New Product")
            name = st.text_input("Product Name")
            category = st.text_input("Category")
            price = st.number_input("Price", min_value=0.0, step=0.25)
            stock = st.number_input("Starting Stock", min_value=0, step=1)
            shelf = st.selectbox("Shelf Type", ["Front Display", "Pastry Case", "Bread Rack", "Storage"])

            if st.button("Add Product"):
                products.append({
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "category": category,
                    "price": price,
                    "stock": stock,
                    "shelf": shelf,
                    "low_stock_flag": False
                })
                with products_path.open("w", encoding="utf-8") as f:
                    json.dump(products, f, indent=2)
                st.success("Product added successfully.")
                st.rerun()

    with tab3:
            st.subheader("Update Price or Restock Inventory")

            if products:
                selected_name = st.selectbox("Select Product", [p["name"] for p in products], key="owner_edit")
                product = find_product_by_name(selected_name)

                if product:
                    new_price = st.number_input("Update Price", min_value=0.0, value=float(product["price"]), step=0.25)
                    restock_amount = st.number_input("Restock Amount", min_value=0, step=1)

                    if st.button("Save Changes"):
                        if update_product(selected_name, new_price, restock_amount):
                            st.success("Product updated.")
                            st.rerun()
                        else:
                            st.error("Could not update product.")
            else:
                st.info("No products available to update.")

    with tab4:
            st.subheader("Delete Discontinued Product")

            if products:
                delete_name = st.selectbox("Choose Product to Delete", [p["name"] for p in products], key="delete_product")
                if st.button("Delete Product"):
                    delete_product(delete_name)
                    st.success("Product deleted.")
                    st.rerun()
            else:
                st.info("No products available to delete.")