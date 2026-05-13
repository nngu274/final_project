import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import uuid
import logging

def load_json(path: Path):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from ui.auth_views import AuthView
from ui.session_manager import SessionManager
from pages.employee_dashboard import EmployeeDashboard

st.set_page_config(page_title="Whimsical Sweets Operations Portal", layout="wide")

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


def render_owner_dashboard(products, products_path, save_json_func):
    st.subheader("Shop Owner Dashboard")
    st.write("Manage inventory and operations with the same clean, tabbed layout as the employee dashboard.")
    st.divider()

    total_products = len(products)
    low_stock_count = sum(1 for p in products if p.get("stock", 0) <= 5)
    total_stock = sum(p.get("stock", 0) for p in products)
    total_value = sum(p.get("price", 0.0) * p.get("stock", 0) for p in products)

    st.write("### 📊 Dashboard Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Products Available", total_products)
    col2.metric("Low Stock Items", low_stock_count, delta="⚠️" if low_stock_count else "✅")
    col3.metric("Stock Units", total_stock)
    col4.metric("Inventory Value", format_price(total_value))

    if low_stock_count > 0:
        st.warning(f"⚠️ {low_stock_count} products need restocking attention.")
    else:
        st.success("✅ Inventory levels look good.")

    tabs = st.tabs(["Catalog", "Add Product", "Update / Restock", "Delete Product", "Analytics", "Alerts", "AI Assistant"])

    with tabs[0]:
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

            total_filtered = len(filtered)
            low_stock_filtered = sum(1 for p in filtered if p.get("stock", 0) <= 5)
            total_stock_filtered = sum(p.get("stock", 0) for p in filtered)
            total_value_filtered = sum(p.get("price", 0.0) * p.get("stock", 0) for p in filtered)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Products", total_filtered)
            col2.metric("Low Stock", low_stock_filtered)
            col3.metric("Stock Units", total_stock_filtered)
            col4.metric("Inventory Value", format_price(total_value_filtered))

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

    with tabs[1]:
        st.markdown("### Add New Product")
        with st.form("owner_add_product_form", clear_on_submit=True):
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
                    save_json_func(products_path, products)
                    st.success(f"Product '{name.strip()}' added successfully.")
                    st.info("Product is now available in the Catalog tab.")

    with tabs[2]:
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

                with st.form("owner_update_product_form"):
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
                            save_json_func(products_path, products)
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

    with tabs[3]:
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
                        save_json_func(products_path, products)
                        st.success(f"Product '{selected_product['name']}' deleted.")
                        st.info("Check the Catalog tab to verify removal.")
            else:
                st.error("Selected product could not be found.")
        else:
            st.info("No products available to delete.")

    with tabs[4]:
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

    with tabs[5]:
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
    with tabs[6]:
        render_ai_chatbot(
            session_key="owner_ai_messages",
            log_file="owner_chat_logs.json",
            title="🤖 AI Operations Assistant",
            subtitle="Ask Robo about products, stock, inventory, prices, or sales.",
            starter_message="Hi! I’m Robo, your Whimsical Sweets assistant. Ask me about products, stock, inventory, prices, or sales."
        )

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

logger.info(f"User {session.current_user_email()} ({session.current_user_role()}) accessed the dashboard")

if st.button("Log Out"):
    logger.info(f"User {session.current_user_email()} logged out")
    session.logout()
    st.rerun()

from pages.owner_dashboard import render_owner_dashboard
if st.session_state["role"] == "Shop Owner":
    render_owner_dashboard(products, products_path, save_json)

elif st.session_state["role"] == "Employee":
    # Initialize and render employee dashboard
    employee_dashboard = EmployeeDashboard(
        products=products,
        sales_log=sales_log,
        products_path=products_path,
        sales_path=sales_path,
        save_json_func=save_json
    )
    employee_dashboard.render()

