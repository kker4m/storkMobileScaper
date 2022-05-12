from typing import List

class Plan:
    name: str or None = None
    operator_name: str
    operator_url: str
    icon_url: str
    duration_days: int
    countries: List[str]
    price: float
    currency: str or None
    size_mb: int
