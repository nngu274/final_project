import streamlit as st
import time

from services.auth_service import AuthService


class AuthView:
    def __init__(self, session_manager):
        self.session = session_manager
        self.auth_service = AuthService()

    def render(self):
        st.title("Whimsical Sweets Operations Portal")

        tab1, tab2 = st.tabs(["Log In", "Create Account"])

        with tab1:
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

        with tab2:
            new_email = st.text_input("New Email", key="register_email")
            new_password = st.text_input("New Password", type="password", key="register_password")
            role = st.selectbox("Role", ["Shop Owner", "Employee"])

            if st.button("Create Account", use_container_width=True):
                success, message = self.auth_service.register(new_email, new_password, role)

                if success:
                    st.success("You've successfully made an account.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(message)