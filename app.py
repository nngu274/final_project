import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid

from ui.session_manager import SessionManager
from ui.auth_views import AuthView

st.set_page_config(page_title="Whimsical Sweets Operations Portal", layout="centered")

products_path = Path("inventory.json")
sales_path = Path("sales.json")

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

session = SessionManager()
session.initialize()

if not session.is_logged_in():
    auth_view = AuthView(session)
    auth_view.render()
    st.stop()

st.title("Whimsical Sweets Operations Portal")
st.write(f"Logged in as: **{session.current_user_email()}**")
st.write(f"Role: **{session.current_user_role()}**")

if st.button("Log Out"):
    session.logout()
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
                with st.container(border=True):
                    st.metric(label="All Products", value=len(products))
                    if len(products) > 0:
                        for product in products:
                            with st.expander(product.get('name')):
                                st.write(f"**ID:** {product.get('id')}")
                                st.write(f"**Name:** {product.get('name')}")
                                st.write(f"**Price:** {product.get('price')}")
                                st.write(f"**Stock**: {product.get('stock')}")
                                st.write(f"**Shelf**: {product.get('shelf')}")
                                st.write(f"**Status**: {product.get('low_stock_flag')}")
                    else:
                        st.info("No Products Yet!")


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

    with tab3:
            st.subheader("Update Price or Restock Inventory")

            if products:
                selected_name = st.selectbox("Select Product", [p["name"] for p in products], key="owner_edit")
                for product in products:
                    if product["name"] == selected_name:
                        product
                    else:
                        None

                if product:
                    new_price = st.number_input("Update Price", min_value=0.0, value=float(product["price"]), step=0.25)
                    restock_amount = st.number_input("Restock Amount", min_value=0, step=1)

                    if st.button("Save Changes"):
                        product["price"] = new_price
                        product["stock"] += restock_amount
                        if product["stock"] > 5:
                            product["low_stock_flag"] = False
                        with products_path.open("w", encoding="utf-8") as f:
                            json.dump(products, f, indent=2)
            else:
                st.info("No products available to update.")

    with tab4:
            st.subheader("Delete Discontinued Product")

            if products:
                delete_name = st.selectbox("Choose Product to Delete", [p["name"] for p in products], key="delete_product")
                if st.button("Delete Product"):
                    products[:] = [p for p in products if p["name"] != delete_name]
                    with products_path.open("w", encoding="utf-8") as f:
                        json.dump(products, f, indent=2)
                    st.success("Product deleted.")
            else:
                st.info("No products available to delete.")

elif st.session_state["role"] == "Employee":
        st.header("Employee Dashboard")

        low_stock_count = len([p for p in products if p.get("stock", 0) <= 5])
        total_stock = sum([p.get("stock", 0) for p in products])
        sales_count = len(sales_log)

        col1, col2, col3 = st.columns(3)
        col1.metric("Products Available", len(products))
        col2.metric("Low Stock Items", low_stock_count)
        col3.metric("Sales Logged", sales_count)

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs([
            "View Catalog",
            "Log Sales",
            "Flag Low Stock",
            "Training"
        ])

        with tab1:
            st.subheader("Current Catalog")
            if products:
                st.dataframe(products, width="stretch")
            else:
                st.info("No products available.")

        with tab2:
            st.subheader("Log Daily Sales")

            if products:
                sale_product_name = st.selectbox("Select Product Sold", [p["name"] for p in products], key="sale_product")
                quantity_sold = st.number_input("Quantity Sold", min_value=1, step=1)

                if st.button("Record Sale"):
                    for product in products:
                        if product["name"] == sale_product_name:
                            if quantity_sold <= product["stock"]:
                                product["stock"] -= quantity_sold

                                if product["stock"] <= 5:
                                    product["low_stock_flag"] = True

                                sales_log.append({
                                    "id": str(uuid.uuid4()),
                                    "product_name": product["name"],
                                    "quantity_sold": quantity_sold,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })

                                with products_path.open("w", encoding="utf-8") as f:
                                    json.dump(products, f, indent=2)
                                with sales_path.open("w", encoding="utf-8") as f:
                                    json.dump(sales_log, f, indent=2)
                                st.success("Sale recorded successfully.")
                                st.rerun()
                            else:
                                st.error("Not enough stock available.")
                                

        with tab3:
            st.subheader("Flag Items Running Dangerously Low")

            low_items = [p for p in products if p["stock"] <= 5]

            if low_items:
                for item in low_items:
                    st.warning(f"{item['name']} is low on stock. Only {item['stock']} left.")
            else:
                st.success("No low-stock items right now.")

        with tab4:
            st.subheader("New Employee Training")
            st.markdown("""
            ### Bakery Basics
            - Always rotate stock using first-in, first-out.
            - Record sales accurately at the end of each shift.
            - Flag low-stock items before they run out.
            - Keep display shelves neat and labeled correctly.
            - Report damaged or stale products to the Shop Owner.
            """)

