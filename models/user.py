from dataclasses import dataclass, asdict
import uuid

@dataclass
class User:
    email: str
    password: str
    role: str
    id: str | None = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(id=data.get("id"), email=data.get("email", ""), password=data.get("password", ""), role=data.get("role", "Employee"))
