import streamlit as st

from ui.session_manager import SessionManager
from services.ai_chat_service import AIChatService

session = SessionManager()
session.require_role(["Shop Owner", "Employee"])

st.title("AI Operations Assistant")

ai_service = AIChatService()

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

for message in st.session_state["chat_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask the assistant...")

if question:

    st.session_state["chat_messages"].append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    response = ai_service.ask(question)

    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.write(response)