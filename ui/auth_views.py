"""
Authentication UI components
"""
import streamlit as st
import time

from services.auth_service import AuthService

class AuthView:
    """Handles login and registration UI."""

    def __init__(self, session_manager):
        """Initialize with session manager."""
        self.session = session_manager
        self.auth_service = AuthService()

    def render(self):
        """Render the authentication interface."""
        st.title("Whimsical Sweets Operations Portal")

        tab1, tab2 = st.tabs(["Log In", "Create Account"])

        with tab1:
            self._render_login_tab()

        with tab2:
            self._render_register_tab()

    def _render_login_tab(self):
        """Render the login form."""
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log In", use_container_width=True):
            user = self.auth_service.login(email, password)

            if user:
                st.success("You have logged in.")
                time.sleep(1.5)

                self.session.login(user)
                st.rerun()
            else:
                st.error("Invalid credentials.")

    def _render_register_tab(self):
        """Render the registration form."""
        new_email = st.text_input("New Email", key="register_email")
        new_password = st.text_input("New Password", type="password", key="register_password")
        role = st.selectbox("Role", ["Shop Owner", "Employee"], key="register_role")

        if st.button("Create Account", use_container_width=True):
            success, message = self.auth_service.register(new_email, new_password, role)

            if success:
                st.success("You've successfully made an account.")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error(message)