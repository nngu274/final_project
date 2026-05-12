"""
Session management for user authentication state
"""
import streamlit as st
from models.user import User

class SessionManager:
    """Manages user session state in Streamlit."""

    def initialize(self):
        """Initialize session state with default values."""
        defaults = {
            "logged_in": False,
            "user": None,
            "role": None,
            "chat_messages": []
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def login(self, user: User):
        """Log in a user and update session state."""
        st.session_state["logged_in"] = True
        st.session_state["user"] = user.to_dict()
        st.session_state["role"] = user.role

    def logout(self):
        """Log out the current user."""
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.session_state["chat_messages"] = []

    def is_logged_in(self) -> bool:
        """Check if a user is logged in."""
        return bool(st.session_state.get("logged_in"))

    def current_user(self) -> dict:
        """Get the current user data."""
        return st.session_state.get("user")

    def current_user_email(self) -> str:
        """Get the current user's email."""
        user = self.current_user()
        return user.get("email", "Unknown") if user else "Unknown"

    def current_user_role(self) -> str:
        """Get the current user's role."""
        return st.session_state.get("role", "Unknown")

    def require_login(self):
        """Require login, stop execution if not logged in."""
        self.initialize()
        if not self.is_logged_in():
            st.warning("Please log in from the Home page first.")
            st.stop()

    def require_role(self, allowed_roles: list):
        """Require specific roles, stop execution if not authorized."""
        self.require_login()
        if self.current_user_role() not in allowed_roles:
            st.error("You do not have permission to view this page.")
            st.stop()