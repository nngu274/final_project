import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import uuid

from ui.auth_views import AuthView
from ui.session_manager import SessionManager
from services.employee_service import calculate_low_stock, record_sale

st.set_page_config(page_title="Whimsical Sweets Operations Portal", layout="centered")

products_path = Path("inventory.json")
sales_path = Path("sales.json")


def load_json(path: Path):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def format_price(value):
    return f"${value:,.2f}"


def product_option_label(product):
    return f"{product['name']} ({product['id'][:8]})"


def find_product_by_id(products, product_id):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def filter_products(products, search_text, category, shelf):
    filtered = []
    search_text = search_text.lower().strip()
    for product in products:
        if search_text:
            if search_text not in product["name"].lower() and search_text not in product["category"].lower():
                continue
        if category != "All" and product["category"] != category:
            continue
        if shelf != "All" and product["shelf"] != shelf:
            continue
        filtered.append(product)
    return filtered


def sort_products(products, sort_key, ascending=True):
    if sort_key == "Name":
        return sorted(products, key=lambda p: p["name"].lower(), reverse=not ascending)
    if sort_key == "Price":
        return sorted(products, key=lambda p: p["price"], reverse=not ascending)
    if sort_key == "Stock":
        return sorted(products, key=lambda p: p["stock"], reverse=not ascending)
    return products


products = load_json(products_path)
sales_log = load_json(sales_path)

session = SessionManager()
session.initialize()

if "owner_page" not in st.session_state:
    st.session_state["owner_page"] = "Catalog"

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
    st.subheader("Shop Owner Dashboard")
    owner_pages = ["Catalog", "Add Product", "Update / Restock", "Delete Product", "Analytics", "Alerts"]
    st.session_state["owner_page"] = st.selectbox("Choose Owner Page", owner_pages, index=owner_pages.index(st.session_state["owner_page"]))

    current_page = st.session_state["owner_page"]

    if current_page == "Catalog":
        st.markdown("### Catalog Overview")
        if products:
            categories = ["All"] + sorted({p["category"] for p in products if p.get("category")})
            shelves = ["All"] + sorted({p["shelf"] for p in products if p.get("shelf")})
            search_text = st.text_input("Search products", key="owner_catalog_search")
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                category_filter = st.selectbox("Filter by Category", categories, key="owner_catalog_category")
            with col2:
                shelf_filter = st.selectbox("Filter by Shelf", shelves, key="owner_catalog_shelf")
            with col3:
                sort_key = st.selectbox("Sort by", ["Name", "Price", "Stock"], key="owner_catalog_sort")
                sort_desc = st.checkbox("Descending", value=False, key="owner_catalog_desc")

            filtered = filter_products(products, search_text, category_filter, shelf_filter)
            filtered = sort_products(filtered, sort_key, not sort_desc)

            total_products = len(filtered)
            low_stock_count = sum(1 for p in filtered if p.get("stock", 0) <= 5)
            total_stock = sum(p.get("stock", 0) for p in filtered)
            total_value = sum(p.get("price", 0.0) * p.get("stock", 0) for p in filtered)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Products", total_products)
            col2.metric("Low Stock", low_stock_count)
            col3.metric("Stock Units", total_stock)
            col4.metric("Inventory Value", format_price(total_value))

            st.divider()
            display_data = [
                {
                    "ID": p["id"][:8] + "...",
                    "Name": p["name"],
                    "Category": p["category"],
                    "Price": format_price(p["price"]),
                    "Stock": p["stock"],
                    "Shelf": p["shelf"],
                    "Low Stock": "Yes" if p.get("stock", 0) <= 5 else "No",
                }
                for p in filtered
            ]
            st.dataframe(display_data, use_container_width=True)
        else:
            st.info("No products found in inventory. Add a product to begin.")

    elif current_page == "Add Product":
        st.markdown("### Add New Product")
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name", key="owner_add_name")
                category = st.text_input("Category", key="owner_add_category")
                shelf = st.selectbox("Shelf Type", ["Front Display", "Pastry Case", "Bread Rack", "Storage"], key="owner_add_shelf")
            with col2:
                price = st.number_input("Price ($)", min_value=0.0, step=0.25, format="%.2f", key="owner_add_price")
                stock = st.number_input("Starting Stock", min_value=0, step=1, key="owner_add_stock")
            submitted = st.form_submit_button("Add Product")

            if submitted:
                errors = []
                if not name.strip():
                    errors.append("Product name is required.")
                if not category.strip():
                    errors.append("Category is required.")
                if price < 0:
                    errors.append("Price cannot be negative.")
                if stock < 0:
                    errors.append("Stock cannot be negative.")
                if any(p["name"].strip().lower() == name.strip().lower() for p in products):
                    errors.append("A product with this name already exists.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    products.append({
                        "id": str(uuid.uuid4()),
                        "name": name.strip(),
                        "category": category.strip(),
                        "price": price,
                        "stock": stock,
                        "shelf": shelf,
                        "low_stock_flag": stock <= 5,
                        "created_at": datetime.now().isoformat(),
                    })
                    save_json(products_path, products)
                    st.success(f"Product '{name.strip()}' added successfully.")
                    st.info("Product is now available in the Catalog tab.")

    elif current_page == "Update / Restock":
        st.markdown("### Update or Restock a Product")
        if products:
            product_map = {product_option_label(p): p["id"] for p in products}
            selected_option = st.selectbox("Select product to update", list(product_map.keys()), key="owner_update_select")
            selected_id = product_map[selected_option]
            selected_product = find_product_by_id(products, selected_id)

            if selected_product:
                st.write("**Current Product Details**")
                st.write(f"- Name: {selected_product['name']}")
                st.write(f"- Category: {selected_product['category']}")
                st.write(f"- Price: {format_price(selected_product['price'])}")
                st.write(f"- Stock: {selected_product['stock']}")
                st.write(f"- Shelf: {selected_product['shelf']}")
                st.write(f"- Low Stock: {'Yes' if selected_product.get('stock', 0) <= 5 else 'No'}")

                with st.form("update_product_form"):
                    new_price = st.number_input("New Price ($)", min_value=0.0, value=float(selected_product["price"]), step=0.25, format="%.2f", key="owner_update_price")
                    restock_amount = st.number_input("Restock Amount", min_value=0, value=0, step=1, key="owner_restock_amount")
                    submitted = st.form_submit_button("Save Changes")

                    if submitted:
                        if new_price == selected_product["price"] and restock_amount == 0:
                            st.warning("No changes were made. Update the price or add stock.")
                        else:
                            selected_product["price"] = new_price
                            selected_product["stock"] = selected_product.get("stock", 0) + restock_amount
                            selected_product["low_stock_flag"] = selected_product["stock"] <= 5
                            save_json(products_path, products)
                            st.success("Product updated successfully.")
                            st.write(f"- New Price: {format_price(new_price)}")
                            st.write(f"- New Stock: {selected_product['stock']}")
                            if selected_product["stock"] <= 5:
                                st.warning("Stock is still low after this update.")
                            else:
                                st.info("Stock is now above the low-stock threshold.")
            else:
                st.error("Selected product could not be found.")
        else:
            st.info("No products available to update.")

    elif current_page == "Delete Product":
        st.markdown("### Delete Discontinued Product")
        if products:
            product_map = {product_option_label(p): p["id"] for p in products}
            selected_option = st.selectbox("Choose product to delete", list(product_map.keys()), key="owner_delete_select")
            selected_id = product_map[selected_option]
            selected_product = find_product_by_id(products, selected_id)

            if selected_product:
                st.write("**Product to delete:**")
                st.write(f"- Name: {selected_product['name']}")
                st.write(f"- Category: {selected_product['category']}")
                st.write(f"- Price: {format_price(selected_product['price'])}")
                st.write(f"- Stock: {selected_product['stock']}")
                st.write(f"- Shelf: {selected_product['shelf']}")

                confirm_delete = st.checkbox("I understand this will permanently remove the product.", key="owner_delete_confirm")
                if st.button("Delete Product"):
                    if not confirm_delete:
                        st.warning("Please confirm deletion before proceeding.")
                    else:
                        products[:] = [p for p in products if p["id"] != selected_id]
                        save_json(products_path, products)
                        st.success(f"Product '{selected_product['name']}' deleted.")
                        st.info("Check the Catalog tab to verify removal.")
            else:
                st.error("Selected product could not be found.")
        else:
            st.info("No products available to delete.")

    elif current_page == "Analytics":
        st.markdown("### Inventory Analytics")
        if products:
            total_products = len(products)
            total_stock = sum(p.get("stock", 0) for p in products)
            total_value = sum(p.get("price", 0.0) * p.get("stock", 0) for p in products)
            low_stock = [p for p in products if p.get("stock", 0) <= 5]
            average_price = total_value / total_products if total_products else 0.0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Products", total_products)
            col2.metric("Total Stock", total_stock)
            col3.metric("Inventory Value", format_price(total_value))
            col4.metric("Average Price", format_price(average_price))

            st.divider()
            st.subheader("Low Stock Items")
            if low_stock:
                for product in low_stock:
                    st.warning(f"{product['name']} — {product['stock']} units remaining")
            else:
                st.success("No low stock items at the moment.")

            st.divider()
            st.subheader("Top Products by Stock Value")
            ranked = sorted(products, key=lambda p: p.get("price", 0.0) * p.get("stock", 0), reverse=True)[:5]
            st.table([
                {
                    "Product": p["name"],
                    "Value": format_price(p.get("price", 0.0) * p.get("stock", 0)),
                    "Stock": p.get("stock", 0),
                    "Category": p.get("category", "")
                }
                for p in ranked
            ])
        else:
            st.info("No inventory data available.")

    elif current_page == "Alerts":
        st.markdown("### Alerts & Recommendations")
        threshold = st.number_input("Low stock threshold", min_value=1, value=5, step=1, key="owner_alert_threshold")
        if products:
            low_stock = [p for p in products if p.get("stock", 0) <= threshold]
            if low_stock:
                for product in low_stock:
                    st.warning(f"{product['name']} is low ({product['stock']} units). Consider restocking.")
                    recommended = max(threshold * 2 - product["stock"], 0)
                    if recommended > 0:
                        st.info(f"Recommended restock: {recommended} units.")
            else:
                st.success("No current alerts. Inventory is above threshold.")
        else:
            st.info("No products available to generate alerts.")

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
                success, message = record_sale(
                    products,
                    sales_log,
                    sale_product_name,
                    quantity_sold
                )

                if success:
                    save_json(products_path, products)
                    save_json(sales_path, sales_log)
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with tab3:
        st.subheader("Flag Items Running Dangerously Low")

        low_items = calculate_low_stock(products)
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

