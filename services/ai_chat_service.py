import os
from dotenv import load_dotenv
from openai import OpenAI
from services.owner_service import InventoryDataAccess, InventoryService, StockManagementService


class AIChatService:
    """AI assistant that answers shop questions using inventory data."""

    def __init__(self):
        load_dotenv()
        data_access = InventoryDataAccess()
        self.inventory_service = InventoryService(data_access)
        self.stock_service = StockManagementService(data_access)

    def build_context(self) -> str:
        products_response = self.inventory_service.get_all_products()
        products = products_response.data if products_response.success else []
        low_stock_response = self.stock_service.get_low_stock_items()
        low_stock = low_stock_response.data if low_stock_response.success else []

        product_lines = [
            f"- {p['name']}: category={p['category']}, price=${p['price']:.2f}, stock={p['stock']}, shelf={p['shelf']}, low_stock={p['low_stock_flag']}"
            for p in products
        ]
        low_stock_lines = [f"- {p['name']}: {p['stock']} left" for p in low_stock]

        return f"""
Whimsical Sweets current app data:

Products:
{chr(10).join(product_lines) if product_lines else 'No products yet.'}

Low-stock products:
{chr(10).join(low_stock_lines) if low_stock_lines else 'No low-stock items right now.'}

Recent sales:
No sales data available yet.
"""

    def ask(self, user_question: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._fallback_response(user_question)

        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an operations assistant for Whimsical Sweets, a bakery inventory and sales app. "
                            "Answer using the provided app data. Keep responses short, clear, and useful for shop owners or employees. "
                            "Do not make up inventory that is not in the context."
                        ),
                    },
                    {"role": "user", "content": f"{self.build_context()}\n\nUser question: {user_question}"},
                ],
            )
            return response.choices[0].message.content
        except Exception:
            return self._fallback_response(user_question)

    def _fallback_response(self, user_question: str) -> str:
        products_response = self.inventory_service.get_all_products()
        products = products_response.data if products_response.success else []
        low_stock_response = self.stock_service.get_low_stock_items()
        low_stock = low_stock_response.data if low_stock_response.success else []

        q = user_question.lower()
        if "low" in q or "restock" in q:
            if not low_stock:
                return "No items are currently low on stock."
            return "Low-stock items: " + ", ".join([f"{p['name']} ({p['stock']} left)" for p in low_stock])
        if "product" in q or "catalog" in q:
            if not products:
                return "There are no products in the catalog yet."
            return "Current products: " + ", ".join([p['name'] for p in products])
        return "AI mode is not connected because OPENAI_API_KEY is missing. I can still answer basic inventory questions about products and low-stock items."
