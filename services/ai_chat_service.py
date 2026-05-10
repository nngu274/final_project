import json
from pathlib import Path

products_path = Path("products.json")
sales_path = Path("sales.json")


class AIChatService:

    def load_products(self):
        if products_path.exists():
            with products_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def load_sales(self):
        if sales_path.exists():
            with sales_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def ask(self, question):
        products = self.load_products()
        sales = self.load_sales()

        question = question.lower()

        if "low stock" in question or "restock" in question:
            low_items = [p for p in products if p["stock"] <= 5]

            if not low_items:
                return "No low-stock items right now."

            return "Low-stock items: " + ", ".join(
                [f"{item['name']} ({item['stock']} left)" for item in low_items]
            )

        elif "products" in question or "catalog" in question:
            if not products:
                return "No products available."

            return "Current products: " + ", ".join(
                [p["name"] for p in products]
            )

        elif "sales" in question:
            return f"There are currently {len(sales)} sales records logged."

        else:
            return (
                "I can answer questions about products, sales, "
                "and low-stock inventory."
            )