# models.py
from django.db import models

class StockTransaction(models.Model):
    TRADE_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )

    date = models.DateField()
    company = models.CharField(max_length=100)
    trade_type = models.CharField(max_length=4, choices=TRADE_CHOICES)
    quantity = models.IntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    balance_qty = models.IntegerField()
    split_ratio = models.CharField(max_length=10, null=True, blank=True)  # Updated to CharField



    def __str__(self):
        return f"{self.date} - {self.company} - {self.trade_type} - {self.quantity}"
