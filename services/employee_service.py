"""
Employee service module for business logic operations
Enhanced with validation, error handling, and logging
"""
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import uuid

# Setup logger
logger = logging.getLogger(__name__)

def calculate_low_stock(products: List[Dict], threshold: int = 5) -> List[Dict]:
    """
    Calculate which products are running low on stock.

    Args:
        products: List of product dictionaries
        threshold: Stock level threshold for low stock (default: 5)

    Returns:
        List of products with low stock
    """
    if not products:
        logger.warning("calculate_low_stock called with empty products list")
        return []

    try:
        low_stock_products = [
            p for p in products
            if isinstance(p.get("stock"), (int, float)) and p.get("stock", 0) <= threshold
        ]
        logger.info(f"Found {len(low_stock_products)} products with low stock (≤{threshold})")
        return low_stock_products
    except Exception as e:
        logger.error(f"Error calculating low stock: {e}")
        return []

def record_sale(products: List[Dict], sales_log: List[Dict], product_name: str, quantity_sold: int) -> Tuple[bool, str]:
    """
    Record a sale transaction with validation and error handling.

    Args:
        products: List of product dictionaries (modified in place)
        sales_log: List of sales records (modified in place)
        product_name: Name of the product sold
        quantity_sold: Quantity sold

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Input validation
    if not product_name or not product_name.strip():
        logger.warning("record_sale called with empty product name")
        return False, "Product name cannot be empty."

    if not isinstance(quantity_sold, int) or quantity_sold <= 0:
        logger.warning(f"record_sale called with invalid quantity: {quantity_sold}")
        return False, "Quantity sold must be a positive integer."

    if not products:
        logger.warning("record_sale called with empty products list")
        return False, "No products available."

    # Find the product
    product = None
    for p in products:
        if p.get("name") == product_name.strip():
            product = p
            break

    if not product:
        logger.warning(f"Product not found: {product_name}")
        return False, f"Product '{product_name}' not found."

    # Validate stock availability
    current_stock = product.get("stock", 0)
    if not isinstance(current_stock, (int, float)):
        logger.error(f"Invalid stock value for product {product_name}: {current_stock}")
        return False, "Invalid product stock data."

    if quantity_sold > current_stock:
        logger.warning(f"Insufficient stock for {product_name}: requested {quantity_sold}, available {current_stock}")
        return False, f"Not enough stock available. Only {current_stock} units remaining."

    try:
        # Update product stock
        product["stock"] = current_stock - quantity_sold

        # Update low stock flag
        product["low_stock_flag"] = product["stock"] <= 5

        # Record the sale
        sale_record = {
            "id": str(uuid.uuid4()),
            "product_name": product_name.strip(),
            "quantity_sold": quantity_sold,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        sales_log.append(sale_record)

        logger.info(f"Sale recorded: {quantity_sold} x {product_name} (remaining stock: {product['stock']})")
        return True, "Sale recorded successfully."

    except Exception as e:
        logger.error(f"Error recording sale for {product_name}: {e}")
        return False, f"An error occurred while recording the sale: {str(e)}"

def validate_product_data(product: Dict) -> Tuple[bool, str]:
    """
    Validate product data structure.

    Args:
        product: Product dictionary to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    required_fields = ["name", "price", "stock"]
    for field in required_fields:
        if field not in product:
            return False, f"Missing required field: {field}"

    if not product.get("name") or not product["name"].strip():
        return False, "Product name cannot be empty"

    if not isinstance(product.get("price"), (int, float)) or product["price"] < 0:
        return False, "Product price must be a non-negative number"

    if not isinstance(product.get("stock"), (int, float)) or product["stock"] < 0:
        return False, "Product stock must be a non-negative number"

    return True, ""

def get_sales_summary(sales_log: List[Dict]) -> Dict:
    """
    Generate a summary of sales data.

    Args:
        sales_log: List of sales records

    Returns:
        Dictionary with sales summary statistics
    """
    if not sales_log:
        return {"total_sales": 0, "total_quantity": 0, "unique_products": 0}

    total_quantity = sum(sale.get("quantity_sold", 0) for sale in sales_log)
    unique_products = len(set(sale.get("product_name", "") for sale in sales_log))

    return {
        "total_sales": len(sales_log),
        "total_quantity": total_quantity,
        "unique_products": unique_products
    }