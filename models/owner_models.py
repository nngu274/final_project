from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CreateProductRequest:
    name: str
    category: str
    price: float
    stock: int
    shelf: str


@dataclass
class UpdateProductRequest:
    price: Optional[float] = None
    stock_adjustment: Optional[int] = None
    category: Optional[str] = None
    shelf: Optional[str] = None


@dataclass
class ProductResponse:
    id: str
    name: str
    category: str
    price: float
    stock: int
    shelf: str
    low_stock_flag: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductResponse":
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            price=float(data["price"]),
            stock=int(data["stock"]),
            shelf=data["shelf"],
            low_stock_flag=bool(data.get("low_stock_flag", False)),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["created_at"] = self.created_at
        payload["updated_at"] = self.updated_at
        return payload


@dataclass
class InventoryMetrics:
    total_products: int
    total_stock_units: int
    total_inventory_value: float
    low_stock_items_count: int
    average_price: float


@dataclass
class ServiceResponse:
    success: bool
    message: str = ""
    data: Optional[Any] = None
    errors: Optional[List[Dict[str, str]]] = None


@dataclass
class ValidationError:
    field: str
    message: str
    code: str
