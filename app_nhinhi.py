import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

#st.set_page_config(page_title="Whimiscal Sweets")

st.set_page_config(page_title="Course Manager", layout="centered")


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"