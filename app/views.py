# views.py

from rest_framework.response import Response
from rest_framework import status
from .models import StockTransaction
from .serializers import StockTransactionSerializer
from rest_framework.views import APIView
from rest_framework import generics
from .utils import calculate_fifo_inventory, calculate_fifo_average_price

class StockTransactionListCreateView(generics.ListAPIView,generics.CreateAPIView):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer

class StockTransactionListCreateViewUpdate(generics.UpdateAPIView,generics.DestroyAPIView):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer
    lookup_field='id'

class VWAPView(APIView):
    def get(self, request, company, format=None):
        transactions = StockTransaction.objects.filter(company=company)
        total_volume_price = 0
        total_volume = 0

        for transaction in transactions:
            volume_price = transaction.quantity * transaction.price_per_share
            total_volume_price += volume_price
            total_volume += transaction.quantity

        if total_volume == 0:
            return Response({"error": "No transactions for the specified company."}, status=400)

        vwap = total_volume_price / total_volume
        return Response({"vwap": vwap}, status=200)

class FIFOInventoryView(APIView):
    def get(self, request):
        transactions_fifo = StockTransaction.objects.all()
        serializer = StockTransactionSerializer(transactions_fifo, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StockTransactionSerializer(data=request.data)

        if serializer.is_valid():
            trade_type = serializer.validated_data['trade_type']
            quantity = serializer.validated_data['quantity']
            company = serializer.validated_data['company']

            if trade_type == 'SELL':
                remaining_quantity = quantity

                # Retrieve buy transactions in FIFO order
                buy_transactions = StockTransaction.objects.filter(
                    company=company,
                    trade_type='BUY'
                ).order_by('date')

                for transaction in buy_transactions:
                    if remaining_quantity > 0:
                        if transaction.quantity <= remaining_quantity:
                            remaining_quantity -= transaction.quantity
                            transaction.delete()
                        else:
                            transaction.quantity -= remaining_quantity
                            transaction.save()
                            remaining_quantity = 0

            serializer.save()

            # Calculate FIFO Inventory after the transaction
            remaining_inventory = calculate_fifo_inventory(company)

            return Response({
                "message": "Transaction successful.",
                "fifo_inventory": remaining_inventory
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class FIFOAveragePriceView(APIView):
#     def get(self, request, company, quantity, format=None):
#         try:
#             fifo_average_price = calculate_fifo_average_price(company, quantity)
#             return Response({"fifo_average_price": fifo_average_price}, status=200)
#         except ValueError as e:
#             return Response({"error": str(e)}, status=400)
        
class FIFOAveragePriceView(APIView):
    def get(self, request, company, format=None):
        fifo_average_price, total_quantity = calculate_fifo_average_price(company)

        return Response({
            "fifo_average_price": fifo_average_price,
            "fifo_inventory": total_quantity
        }, status=status.HTTP_200_OK)
    
# class StockSplitView(APIView):
#     def get(self, request, company, split_ratio,format=None):
#         split_ratio = StockTransaction.objects.get(company=company).split_ratio

#         if not split_ratio:
#             return Response({"error": "Split ratio is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Parse and validate the split ratio
#             split_ratio = [int(part) for part in split_ratio.split(':')]
#             if len(split_ratio) != 2 or split_ratio[1] <= 0:
#                 raise ValueError("Invalid split ratio.")
#         except ValueError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         # Perform the stock split
#         self.perform_stock_split(company, split_ratio)

#         return Response({"message": f"Stock split for {company} completed successfully."}, status=status.HTTP_201_CREATED)

#     def perform_stock_split(self, company, split_ratio):
#         transactions = StockTransaction.objects.filter(company=company)

#         for transaction in transactions:
#             new_quantity = transaction.quantity * split_ratio[1] // split_ratio[0]
#             transaction.quantity = new_quantity
#             transaction.split_ratio = f"{split_ratio[0]}:{split_ratio[1]}"  # Store the split ratio
#             transaction.save()

class StockSplitView(APIView):
    def get(self, request, company, split_ratio, format=None):
        # split_ratio = StockTransaction.objects.get(company=company).split_ratio
        # Check if the split_ratio is provided in the request data
        if not split_ratio:
            return Response({"error": "Split ratio is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse and validate the split ratio
            split_ratio = [int(part) for part in split_ratio.split(':')]
            if len(split_ratio) != 2 or split_ratio[1] <= 0:
                raise ValueError("Invalid split ratio.")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Perform the stock split
        self.perform_stock_split(company, split_ratio)

        return Response({"message": f"Stock split for {company} completed successfully."}, status=status.HTTP_201_CREATED)

    def perform_stock_split(self, company, split_ratio):
        try:
            # Get the latest StockTransaction for the specified company
            transaction = StockTransaction.objects.filter(company=company).latest('date')

            # Perform the stock split
            new_quantity = transaction.quantity * split_ratio[1] // split_ratio[0]
            transaction.quantity = new_quantity
            transaction.split_ratio = f"{split_ratio[0]}:{split_ratio[1]}"  # Store the split ratio
            transaction.save()

        except StockTransaction.DoesNotExist:
            raise ValueError(f"No StockTransaction found for company: {company}")
