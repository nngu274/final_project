"""
Authentication service for user management
"""
import json
import uuid
from pathlib import Path
from models.user import User

USERS_PATH = Path("users.json")

class AuthService:
    """Handles user authentication and registration."""

    def load_users(self):
        """Load users from JSON file."""
        if USERS_PATH.exists():
            with USERS_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_users(self, users):
        """Save users to JSON file."""
        with USERS_PATH.open("w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)

    def login(self, email, password):
        """Authenticate a user."""
        users = self.load_users()
        clean_email = email.strip().lower()

        for user in users:
            if user["email"].strip().lower() == clean_email and user["password"] == password:
                return User(
                    id=user["id"],
                    email=user["email"],
                    password=user["password"],
                    role=user["role"]
                )

        return None

    def register(self, email, password, role):
        """Register a new user."""
        users = self.load_users()
        clean_email = email.strip().lower()

        if not clean_email or not password:
            return False, "Please enter an email and password."

        if any(user["email"].strip().lower() == clean_email for user in users):
            return False, "There is already a user with this email."

        users.append({
            "id": str(uuid.uuid4()),
            "email": clean_email,
            "password": password,
            "role": role
        })

        self.save_users(users)
        return True, "Account created successfully."