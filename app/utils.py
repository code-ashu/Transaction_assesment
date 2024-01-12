from .models import StockTransaction

def calculate_fifo_inventory(company):
    # Calculate FIFO Inventory after the transaction
    fifo_inventory = 0
    buy_transactions = StockTransaction.objects.filter(
        company=company,
        trade_type='BUY'
    ).order_by('date')

    for transaction in buy_transactions:
        fifo_inventory += transaction.quantity

    return fifo_inventory

def calculate_fifo_average_price(company):
    # Calculate FIFO Average Price and Inventory after the transaction
    total_quantity = 0
    total_value = 0

    buy_transactions = StockTransaction.objects.filter(
        company=company,
        trade_type='BUY'
    ).order_by('date')

    for transaction in buy_transactions:
        total_quantity += transaction.quantity
        total_value += transaction.quantity * transaction.price_per_share

    fifo_average_price = total_value / total_quantity if total_quantity > 0 else 0

    return fifo_average_price, total_quantity
