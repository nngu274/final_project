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

