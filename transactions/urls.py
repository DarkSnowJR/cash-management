from django.urls import path
from .views import TransactionListCreateView, TransactionRetrieveUpdateDestroyView, monthly_summary_report, \
    category_wise_expense_report


urlpatterns = [
    path('transactions/', TransactionListCreateView.as_view(), name='transaction_list_create'),
    path('transactions/<int:pk>/', TransactionRetrieveUpdateDestroyView.as_view(), name='transaction_retrieve_update_destroy'),
    path('reports/monthly-summary/', monthly_summary_report, name='monthly-summary-report'),
    path('reports/category-wise-expense/', category_wise_expense_report, name='category-wise-expense-report'),
]
