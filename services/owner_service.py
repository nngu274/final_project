import json
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from models.owner_models import (
    CreateProductRequest,
    InventoryMetrics,
    ProductResponse,
    ServiceResponse,
    UpdateProductRequest,
    ValidationError,
)


def _iso_timestamp() -> str:
    return datetime.now().isoformat()


class InventoryDataAccess:
    """Direct inventory data access without a separate repository package."""

    def __init__(self, file_path: str = "inventory.json"):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()

    def create(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            products = self._load()
            product_data["id"] = str(uuid.uuid4())
            product_data["created_at"] = _iso_timestamp()
            product_data["updated_at"] = _iso_timestamp()
            products.append(product_data)
            self._save(products)
            return product_data

    def read(self, product_id: str) -> Optional[Dict[str, Any]]:
        products = self._load()
        for product in products:
            if product["id"] == product_id:
                return product
        return None

    def update(self, product_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            products = self._load()
            for index, product in enumerate(products):
                if product["id"] == product_id:
                    product_data["id"] = product_id
                    product_data["created_at"] = product.get("created_at", _iso_timestamp())
                    product_data["updated_at"] = _iso_timestamp()
                    products[index] = product_data
                    self._save(products)
                    return product_data
        raise ValueError(f"Product {product_id} not found")

    def delete(self, product_id: str) -> bool:
        with self._lock:
            products = self._load()
            filtered = [p for p in products if p["id"] != product_id]
            if len(filtered) == len(products):
                return False
            self._save(filtered)
            return True

    def read_all(self) -> List[Dict[str, Any]]:
        return self._load()

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        name_key = name.lower().strip()
        for product in self._load():
            if product.get("name", "").lower().strip() == name_key:
                return product
        return None

    def _load(self) -> List[Dict[str, Any]]:
        if self.file_path.exists():
            with self.file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self, products: List[Dict[str, Any]]):
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(products, f, indent=2)


class InventoryService:
    """Core inventory operations for shop owner backend."""

    def __init__(self, data_access: InventoryDataAccess):
        self.data_access = data_access

    def create_product(self, request: CreateProductRequest) -> ServiceResponse:
        errors = self._validate_product_data(request)
        if errors:
            return ServiceResponse(success=False, message="Validation failed", errors=[e.__dict__ for e in errors])

        if self.data_access.find_by_name(request.name):
            return ServiceResponse(success=False, message="Product with this name already exists")

        product = {
            "name": request.name.strip(),
            "category": request.category.strip(),
            "price": float(request.price),
            "stock": int(request.stock),
            "shelf": request.shelf.strip(),
            "low_stock_flag": int(request.stock) <= 5,
        }

        saved = self.data_access.create(product)
        return ServiceResponse(success=True, message="Product created successfully", data=ProductResponse.from_dict(saved).to_dict())

    def update_product(self, product_id: str, request: UpdateProductRequest) -> ServiceResponse:
        product = self.data_access.read(product_id)
        if not product:
            return ServiceResponse(success=False, message="Product not found")

        if request.price is not None and request.price < 0:
            return ServiceResponse(success=False, message="Price cannot be negative")
        if request.stock_adjustment is not None and request.stock_adjustment < 0:
            return ServiceResponse(success=False, message="Stock adjustment cannot be negative")

        if request.category is not None:
            product["category"] = request.category.strip()
        if request.shelf is not None:
            product["shelf"] = request.shelf.strip()
        if request.price is not None:
            product["price"] = float(request.price)
        if request.stock_adjustment is not None:
            product["stock"] = int(product.get("stock", 0)) + int(request.stock_adjustment)

        product["low_stock_flag"] = int(product.get("stock", 0)) <= 5
        updated = self.data_access.update(product_id, product)

        return ServiceResponse(success=True, message="Product updated successfully", data=ProductResponse.from_dict(updated).to_dict())

    def delete_product(self, product_id: str) -> ServiceResponse:
        product = self.data_access.read(product_id)
        if not product:
            return ServiceResponse(success=False, message="Product not found")

        deleted = self.data_access.delete(product_id)
        if not deleted:
            return ServiceResponse(success=False, message="Product could not be deleted")

        return ServiceResponse(success=True, message=f"Product '{product.get('name', '')}' deleted successfully")

    def get_product(self, product_id: str) -> ServiceResponse:
        product = self.data_access.read(product_id)
        if not product:
            return ServiceResponse(success=False, message="Product not found")
        return ServiceResponse(success=True, data=ProductResponse.from_dict(product).to_dict())

    def get_all_products(self) -> ServiceResponse:
        products = [ProductResponse.from_dict(p).to_dict() for p in self.data_access.read_all()]
        return ServiceResponse(success=True, data=products)

    def _validate_product_data(self, request: CreateProductRequest) -> List[ValidationError]:
        errors: List[ValidationError] = []
        if not request.name or not request.name.strip():
            errors.append(ValidationError(field="name", message="Product name is required", code="EMPTY_NAME"))
        if not request.category or not request.category.strip():
            errors.append(ValidationError(field="category", message="Category is required", code="EMPTY_CATEGORY"))
        if request.price < 0:
            errors.append(ValidationError(field="price", message="Price cannot be negative", code="NEGATIVE_PRICE"))
        if request.stock < 0:
            errors.append(ValidationError(field="stock", message="Stock cannot be negative", code="NEGATIVE_STOCK"))
        valid_shelves = ["Front Display", "Pastry Case", "Bread Rack", "Storage"]
        if request.shelf not in valid_shelves:
            errors.append(ValidationError(field="shelf", message=f"Shelf must be one of: {', '.join(valid_shelves)}", code="INVALID_SHELF"))
        return errors


class StockManagementService:
    """Stock-focused backend operations for shop owner."""

    def __init__(self, data_access: InventoryDataAccess):
        self.data_access = data_access

    def get_low_stock_items(self, threshold: int = 5) -> ServiceResponse:
        products = self.data_access.read_all()
        low_stock = [ProductResponse.from_dict(p).to_dict() for p in products if int(p.get("stock", 0)) <= threshold]
        return ServiceResponse(success=True, data=low_stock)

    def restock_product(self, product_id: str, quantity: int) -> ServiceResponse:
        if quantity <= 0:
            return ServiceResponse(success=False, message="Restock quantity must be greater than 0")

        product = self.data_access.read(product_id)
        if not product:
            return ServiceResponse(success=False, message="Product not found")

        product["stock"] = int(product.get("stock", 0)) + quantity
        product["low_stock_flag"] = int(product["stock"]) <= 5
        updated = self.data_access.update(product_id, product)
        return ServiceResponse(success=True, message="Product restocked successfully", data=ProductResponse.from_dict(updated).to_dict())


class AnalyticsService:
    """Business intelligence service for inventory metrics."""

    def __init__(self, data_access: InventoryDataAccess):
        self.data_access = data_access

    def get_inventory_metrics(self) -> ServiceResponse:
        products = [ProductResponse.from_dict(p).to_dict() for p in self.data_access.read_all()]
        total_products = len(products)
        total_stock_units = sum(int(p["stock"]) for p in products)
        total_inventory_value = sum(float(p["price"]) * int(p["stock"]) for p in products)
        low_stock_items_count = sum(1 for p in products if bool(p["low_stock_flag"]))
        average_price = total_inventory_value / total_products if total_products else 0.0

        metrics = InventoryMetrics(
            total_products=total_products,
            total_stock_units=total_stock_units,
            total_inventory_value=total_inventory_value,
            low_stock_items_count=low_stock_items_count,
            average_price=average_price,
        )
        return ServiceResponse(success=True, data=metrics.__dict__)

    def get_category_breakdown(self) -> ServiceResponse:
        products = [ProductResponse.from_dict(p).to_dict() for p in self.data_access.read_all()]
        breakdown: Dict[str, Dict[str, Any]] = {}
        for product in products:
            category = product["category"]
            if category not in breakdown:
                breakdown[category] = {"count": 0, "total_stock": 0, "total_value": 0.0}
            breakdown[category]["count"] += 1
            breakdown[category]["total_stock"] += int(product["stock"])
            breakdown[category]["total_value"] += float(product["price"]) * int(product["stock"])
        return ServiceResponse(success=True, data=breakdown)


class PricingService:
    """Price-focused backend operations for shop owner."""

    def __init__(self, data_access: InventoryDataAccess):
        self.data_access = data_access

    def update_price(self, product_id: str, new_price: float) -> ServiceResponse:
        if new_price < 0:
            return ServiceResponse(success=False, message="Price cannot be negative")

        product = self.data_access.read(product_id)
        if not product:
            return ServiceResponse(success=False, message="Product not found")

        old_price = float(product.get("price", 0.0))
        product["price"] = float(new_price)
        product["updated_at"] = _iso_timestamp()
        updated = self.data_access.update(product_id, product)

        percentage_change = ((new_price - old_price) / old_price * 100) if old_price else 0.0
        message = f"Price updated from ${old_price:.2f} to ${new_price:.2f} ({percentage_change:+.1f}%)"
        return ServiceResponse(success=True, message=message, data=ProductResponse.from_dict(updated).to_dict())

    def bulk_update_prices(self, adjustments: Dict[str, float]) -> ServiceResponse:
        results = []
        for product_id, new_price in adjustments.items():
            response = self.update_price(product_id, new_price)
            results.append({"id": product_id, "success": response.success, "message": response.message})
        return ServiceResponse(success=True, data=results)
