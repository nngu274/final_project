import streamlit as st
from models.user import User

class SessionManager:
    """Keeps login state and user role in Streamlit session_state."""
    def initialize(self):
        defaults = {"logged_in": False, "user": None, "role": None, "chat_messages": []}
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def login(self, user: User):
        st.session_state["logged_in"] = True
        st.session_state["user"] = user.to_dict()
        st.session_state["role"] = user.role

    def logout(self):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.session_state["chat_messages"] = []

    def is_logged_in(self) -> bool:
        return bool(st.session_state.get("logged_in"))

    def current_user(self) -> dict | None:
        return st.session_state.get("user")

    def current_user_email(self) -> str:
        user = self.current_user()
        return user.get("email", "Unknown") if user else "Unknown"

    def current_user_role(self) -> str:
        return st.session_state.get("role", "Unknown")

    def require_login(self):
        self.initialize()
        if not self.is_logged_in():
            st.warning("Please log in from the Home page first.")
            st.stop()

    def require_role(self, allowed_roles: list[str]):
        self.require_login()
        if self.current_user_role() not in allowed_roles:
            st.error("You do not have permission to view this page.")
            st.stop()
