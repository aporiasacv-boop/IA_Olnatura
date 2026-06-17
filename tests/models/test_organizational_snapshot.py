import json
from datetime import date
from decimal import Decimal

from app.models.organizational_snapshot import OrganizationalSnapshot


def test_organizational_snapshot_to_dict() -> None:
    snapshot = OrganizationalSnapshot(
        id=1,
        snapshot_date=date(2025, 6, 15),
        total_customers=100,
        total_orders=100,
        total_revenue=Decimal('49722777.13'),
        top_customer='FARMACIAS DE SIMILARES SA DE CV',
        top_customer_share=Decimal('42.20'),
        top_product='ARISTOCAPS-RB',
        top_product_share=Decimal('42.10'),
        executive_insights_json=json.dumps({'risk_flags': ['Concentracion comercial moderada']}),
    )
    payload = snapshot.to_dict()
    assert payload['id'] == 1
    assert payload['snapshot_date'] == '2025-06-15'
    assert payload['total_customers'] == 100
    assert payload['total_revenue'] == '49722777.13'
    assert payload['top_customer'] == 'FARMACIAS DE SIMILARES SA DE CV'
    assert payload['executive_insights']['risk_flags'] == ['Concentracion comercial moderada']
