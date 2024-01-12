# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('api/stock-transactions/', StockTransactionListCreateView.as_view(), name='stock-transaction-list'),
    path('api/stock-transactions/<id>/', StockTransactionListCreateViewUpdate.as_view(), name='stock-transaction-list'),
    path('vwap/<str:company>/', VWAPView.as_view(), name='vwap'),
    path('fifo/', FIFOInventoryView.as_view(), name='fifo-inventory'),
    path('fifo-average-price/<str:company>/', FIFOAveragePriceView.as_view(), name='fifo-average-price'),
    path('api/stock-split/<str:company>/<str:split_ratio>/', StockSplitView.as_view(), name='stock-split')



]
