from decimal import Decimal
from typing import Any

from app.domain.memory_insights import MemoryInsights

class MemoryInsightsService:

    def build_insights(self, current: dict[str, Any], previous: dict[str, Any] | None) -> MemoryInsights:
        if previous is None:
            return MemoryInsights(
                changes=[],
                stable_findings=['Primer snapshot organizacional registrado; no hay periodo anterior para comparar'],
                new_findings=self._initial_findings(current),
            )
        changes: list[str] = []
        stable_findings: list[str] = []
        new_findings: list[str] = []
        current_customers = int(current.get('total_customers', 0))
        previous_customers = int(previous.get('total_customers', 0))
        if current_customers != previous_customers:
            changes.append(f'Clientes: {previous_customers} -> {current_customers}')
        else:
            stable_findings.append('El numero de clientes permanece estable')
        current_orders = int(current.get('total_orders', 0))
        previous_orders = int(previous.get('total_orders', 0))
        if current_orders != previous_orders:
            changes.append(f'Pedidos: {previous_orders} -> {current_orders}')
        else:
            stable_findings.append('El numero de pedidos permanece estable')
        current_revenue = Decimal(str(current.get('total_revenue', '0')))
        previous_revenue = Decimal(str(previous.get('total_revenue', '0')))
        if current_revenue != previous_revenue:
            changes.append(f'Ingresos: {previous_revenue} -> {current_revenue}')
        else:
            stable_findings.append('Los ingresos registrados se mantienen sin cambios significativos')
        current_customer = current.get('top_customer')
        previous_customer = previous.get('top_customer')
        if current_customer and previous_customer and current_customer == previous_customer:
            stable_findings.append(f'La concentracion comercial sigue observandose en {current_customer}')
        elif current_customer != previous_customer:
            changes.append(f'Cliente dominante: {previous_customer} -> {current_customer}')
            if current_customer:
                new_findings.append(f'Nuevo cliente dominante observado: {current_customer}')
        current_product = current.get('top_product')
        previous_product = previous.get('top_product')
        if current_product and previous_product and current_product == previous_product:
            stable_findings.append(f'El producto dominante {current_product} se mantiene')
        elif current_product != previous_product:
            changes.append(f'Producto dominante: {previous_product} -> {current_product}')
        else:
            stable_findings.append('No se detectan cambios significativos en el producto dominante')
        current_share = float(current.get('top_customer_share', 0))
        previous_share = float(previous.get('top_customer_share', 0))
        if abs(current_share - previous_share) >= 1:
            changes.append(f'Participacion del cliente dominante: {previous_share:.1f}% -> {current_share:.1f}%')
        current_flags = set((current.get('executive_insights') or {}).get('risk_flags', []))
        previous_flags = set((previous.get('executive_insights') or {}).get('risk_flags', []))
        for flag in sorted(current_flags & previous_flags):
            stable_findings.append(f'Hallazgo persistente: {flag}')
        for flag in sorted(current_flags - previous_flags):
            new_findings.append(f'Nuevo hallazgo: {flag}')
        for flag in sorted(previous_flags - current_flags):
            changes.append(f'Hallazgo ya no presente: {flag}')
        if not changes and not stable_findings and not new_findings:
            stable_findings.append('No se detectan cambios significativos entre snapshots')
        return MemoryInsights(
            changes=self._dedupe(changes),
            stable_findings=self._dedupe(stable_findings),
            new_findings=self._dedupe(new_findings),
        )

    @staticmethod
    def _initial_findings(current: dict[str, Any]) -> list[str]:
        findings: list[str] = []
        if current.get('top_customer'):
            findings.append(f'Cliente dominante inicial: {current["top_customer"]}')
        if current.get('top_product'):
            findings.append(f'Producto dominante inicial: {current["top_product"]}')
        executive = current.get('executive_insights') or {}
        for flag in executive.get('risk_flags', []):
            findings.append(f'Hallazgo inicial: {flag}')
        return findings

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        return list(dict.fromkeys(items))
