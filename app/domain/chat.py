from enum import Enum

class QuestionCategory(str, Enum):
    VENTAS = 'ventas'
    CLIENTES = 'clientes'
    GENERAL = 'general'

class ChatIntent(str, Enum):
    CUSTOMERS_COUNT = 'customers_count'
    SALES_COUNT = 'sales_count'
    SALES_TOTAL_AMOUNT = 'sales_total_amount'
    SALES_AVERAGE_TICKET = 'sales_average_ticket'
    TOP_CUSTOMERS = 'top_customers'
    UNKNOWN = 'unknown'
