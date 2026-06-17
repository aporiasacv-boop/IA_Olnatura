from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ExecutiveInsights:
    top_customer_share: float
    top_5_customer_share: float
    top_product_share: float
    dominant_customer: str | None
    dominant_product: str | None
    invoice_rate: float
    revenue_concentration: str
    risk_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            'top_customer_share': self.top_customer_share,
            'top_5_customer_share': self.top_5_customer_share,
            'top_product_share': self.top_product_share,
            'dominant_customer': self.dominant_customer,
            'dominant_product': self.dominant_product,
            'invoice_rate': self.invoice_rate,
            'revenue_concentration': self.revenue_concentration,
            'risk_flags': list(self.risk_flags),
        }
