from datetime import datetime
import uuid

def calculate_low_stock(products):
    return [p for p in products if p["stock"] <= 5]


def record_sale(products, sales_log, product_name, quantity_sold):
    for product in products:
        if product["name"] == product_name:

            if quantity_sold > product["stock"]:
                return False, "Not enough stock available."

            product["stock"] -= quantity_sold

            if product["stock"] <= 5:
                product["low_stock_flag"] = True

            sales_log.append({
                "id": str(uuid.uuid4()),
                "product_name": product["name"],
                "quantity_sold": quantity_sold,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            return True, "Sale recorded successfully."

    return False, "Product not found."