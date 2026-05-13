import json
from pathlib import Path
from openai import OpenAI
import os
import streamlit as st
from dotenv import load_dotenv

class ProductDataStore:
    def __init__(self, products_path: str, sales_path: str):
        self.products_path = Path(products_path)
        self.sales_path = Path(sales_path)

    def get_products_as_string(self) -> str:
        if not self.products_path.exists():
            return "[]"

        with open(self.products_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return json.dumps(data, indent=2)

    def get_sales_as_string(self) -> str:
        if not self.sales_path.exists():
            return "[]"

        with open(self.sales_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return json.dumps(data, indent=2)


class ChatLoggerStore:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def load_logs(self) -> list:
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)

        return []

    def save_logs(self, logs: list) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)


class WhimsicalSweetsAssistantBot:
    def __init__(self, api_key: str, products_context: str, sales_context: str):
        self.client = OpenAI(api_key=api_key)
        self.products_context = products_context
        self.sales_context = sales_context

    def build_ai_prompt(self) -> str:
        return (
            "You are a helpful AI assistant for Whimsical Sweets, a small dessert shop.\n"
            "Answer user questions based ONLY on the product inventory and sales data provided below.\n"
            "You can help employees understand product stock, prices, sales records, and inventory trends.\n"
            "If the answer is not available in the provided data, say you do not have enough information.\n"
            "Keep answers short, clear, and useful for a shop employee.\n\n"
            f"PRODUCT INVENTORY DATA:\n{self.products_context}\n\n"
            f"SALES DATA:\n{self.sales_context}"
        )

    def get_ai_response(self, chat_history: list) -> str:
        try:
            ai_prompt = self.build_ai_prompt()

            messages = [
                {"role": "system", "content": ai_prompt}
            ] + chat_history

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.2
            )

            return response.choices[0].message.content

        except Exception:
            return (
                "Sorry, I cannot generate a live AI response right now because the OpenAI API key is missing, invalid, or not active. "
                "The chatbot structure is still set up correctly with the hidden prompt, chat history, and JSON data connection."
            )
def render_ai_chatbot(
    session_key: str,
    log_file: str,
    title: str = "🤖 AI Operations Assistant",
    subtitle: str = "Ask Robo about products, stock, inventory, prices, or sales.",
    starter_message: str = "Hi! I’m Robo, your Whimsical Sweets assistant. Ask me about products, stock, inventory, prices, or sales.",
    reset_each_login: bool = True
):
    st.markdown(f"### {title}")
    st.write(subtitle)

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    # This figures out who is logged in.
    # Change these keys if your app uses a different session_state name.
    current_user = (
        st.session_state.get("username")
        or st.session_state.get("email")
        or st.session_state.get("user_email")
        or "guest"
    )

    login_tracker_key = f"{session_key}_current_user"

    # Reset chat when a new user logs in
    if reset_each_login:
        if st.session_state.get(login_tracker_key) != current_user:
            st.session_state[session_key] = [
                {
                    "role": "assistant",
                    "content": starter_message
                }
            ]
            st.session_state[login_tracker_key] = current_user

    # If chat does not exist yet, start fresh
    if session_key not in st.session_state:
        st.session_state[session_key] = [
            {
                "role": "assistant",
                "content": starter_message
            }
        ]

    data_store = ProductDataStore("inventory.json", "sales.json")
    logger = ChatLoggerStore(log_file)

    products_context = data_store.get_products_as_string()
    sales_context = data_store.get_sales_as_string()

    bot = WhimsicalSweetsAssistantBot(
        api_key=api_key,
        products_context=products_context,
        sales_context=sales_context
    )

    # Display chat messages
    for message in st.session_state[session_key]:
        if message["role"] == "user":
            st.markdown(
                f"""
                <div style="
                    background-color:#e6f4ff;
                    padding:14px;
                    border-radius:18px;
                    margin:10px 0;
                    max-width:75%;
                    margin-left:auto;
                    border:1px solid #cce7ff;
                ">
                    <strong>🙋 You</strong><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="
                    background-color:#f7f1ff;
                    padding:14px;
                    border-radius:18px;
                    margin:10px 0;
                    max-width:75%;
                    border:1px solid #e4d4ff;
                ">
                    <strong>🤖 Robo</strong><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    with st.form(f"{session_key}_form", clear_on_submit=True):
        user_question = st.text_input(
            "Ask Robo something:",
            placeholder="Example: What items are low stock?"
        )

        submitted = st.form_submit_button("Send")

    if submitted and user_question:
        st.session_state[session_key].append({
            "role": "user",
            "content": user_question
        })

        if not api_key:
            response_text = (
                "Sorry, I cannot generate a live AI response right now because the OpenAI API key is missing. "
                "The chatbot structure is still set up correctly with the hidden prompt, chat history, and JSON data connection."
            )
        else:
            response_text = bot.get_ai_response(st.session_state[session_key])

        st.session_state[session_key].append({
            "role": "assistant",
            "content": response_text
        })

        # Save logs only if you want proof of the interaction.
        # This will NOT reload old logs on refresh anymore.
        logs = logger.load_logs()
        logs.append({
            "user_message": user_question,
            "assistant_message": response_text
        })
        logger.save_logs(logs)

        st.rerun()