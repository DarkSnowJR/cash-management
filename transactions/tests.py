import datetime
from django.urls import reverse
from django.utils.timezone import make_aware
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Transaction
from .serializers import TransactionSerializer
from authentication.models import User


class TransactionListCreateViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def create_transaction(self, category='Food', type='expense', amount=50, date=None):
        if date is None:
            date = datetime.date.today()
        return Transaction.objects.create(user=self.user, category=category, type=type, amount=amount, date=date)

    ### Unit Tests ###

    def test_post_create_transaction(self):
        url = reverse('transaction_list_create')
        data = {'category': 'Food', 'type': 'expense', 'amount': 50, 'date': '2023-07-21'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Transaction.objects.get().user, self.user)
        self.assertEqual(Transaction.objects.get().category, 'Food')
        self.assertEqual(Transaction.objects.get().type, 'expense')
        self.assertEqual(Transaction.objects.get().amount, 50)
        self.assertEqual(Transaction.objects.get().date, make_aware(datetime.datetime(2023, 7, 21)))

    def test_get_queryset_with_filters(self):
        # Create some sample transactions
        self.create_transaction(category='Food', type='expense', amount=50, date='2023-07-19')
        self.create_transaction(category='Transport', type='expense', amount=30, date='2023-07-20')
        self.create_transaction(category='Salary', type='income', amount=1000, date='2023-07-21')

        # Test with category filter
        url = reverse('transaction_list_create') + '?category=Food'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['category'], 'Food')

        # Test with type filter
        url = reverse('transaction_list_create') + '?type=income'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'income')

        # Test with date range filter
        url = reverse('transaction_list_create') + '?date_from=2023-07-19&date_to=2023-07-20'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['date'], '2023-07-20')
        self.assertEqual(response.data[1]['date'], '2023-07-19')

    ### Integration Tests ###

    def test_list_transactions_with_pagination(self):
        # Create more than the page size number of transactions
        for i in range(12):
            self.create_transaction(amount=i)

        url = reverse('transaction_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)  # Check pagination size

    def test_list_transactions_without_pagination(self):
        # Create some transactions
        self.create_transaction(amount=100)
        self.create_transaction(amount=200)

        url = reverse('transaction_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('results', response.data)
        self.assertEqual(len(response.data), 2)  # All transactions are listed


class TransactionRetrieveUpdateDestroyViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.transaction = self.create_transaction()

    def create_transaction(self, category='Food', type='expense', amount=50, date=None):
        if date is None:
            date = datetime.date.today()
        return Transaction.objects.create(user=self.user, category=category, type=type, amount=amount, date=date)

    ### Unit Tests ###

    def test_retrieve_transaction(self):
        url = reverse('transaction_retrieve_update_destroy', kwargs={'pk': self.transaction.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = TransactionSerializer(self.transaction)
        self.assertEqual(response.data, serializer.data)

    def test_update_transaction(self):
        url = reverse('transaction_retrieve_update_destroy', kwargs={'pk': self.transaction.pk})
        data = {'category': 'Groceries', 'type': 'expense', 'amount': 60, 'date': '2023-07-21'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.category, 'Groceries')
        self.assertEqual(self.transaction.type, 'expense')
        self.assertEqual(self.transaction.amount, 60)
        self.assertEqual(self.transaction.date, datetime.date(2023, 7, 21))

    def test_delete_transaction(self):
        url = reverse('transaction_retrieve_update_destroy', kwargs={'pk': self.transaction.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(pk=self.transaction.pk).exists())

    ### Integration Tests ###

    def test_retrieve_nonexistent_transaction(self):
        url = reverse('transaction_retrieve_update_destroy', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_transaction(self):
        url = reverse('transaction_retrieve_update_destroy', kwargs={'pk': 999})
        data = {'category': 'Groceries', 'type': 'expense', 'amount': 60, 'date': '2023-07-21'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_transaction(self):
        url = reverse('transaction_retrieve_update_destroy', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_transaction_with_invalid_data(self):
        url = reverse('transaction_retrieve_update_destroy', kwargs={'pk': self.transaction.pk})
        data = {'category': '', 'type': 'expense', 'amount': -10, 'date': 'invalid_date'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MonthlySummaryReportViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def create_transaction(self, category='Food', type='expense', amount=50, date=None):
        if date is None:
            date = datetime.date.today()
        return Transaction.objects.create(user=self.user, category=category, type=type, amount=amount, date=date)

    ### Unit Tests ###

    def test_monthly_summary_report_response_format(self):
        url = reverse('monthly-summary-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

        if len(response.data) > 0:
            # Check each item in the response list has the correct keys
            first_item = response.data[0]
            self.assertIn('date__year', first_item)
            self.assertIn('date__month', first_item)
            self.assertIn('type', first_item)
            self.assertIn('total_amount', first_item)

    ### Integration Tests ###

    def test_monthly_summary_report(self):
        # Create some sample transactions
        self.create_transaction(category='Food', type='expense', amount=50, date='2023-07-19')
        self.create_transaction(category='Transport', type='expense', amount=30, date='2023-07-20')
        self.create_transaction(category='Salary', type='income', amount=1000, date='2023-08-21')

        url = reverse('monthly-summary-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two distinct months (July and August)

        # Check the correctness of the data returned
        expected_data = [
            {'date__year': 2023, 'date__month': 7, 'type': 'expense', 'total_amount': 80},
            {'date__year': 2023, 'date__month': 8, 'type': 'income', 'total_amount': 1000}
        ]

        self.assertEqual(response.data, expected_data)


class CategoryWiseExpenseReportViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def create_transaction(self, category='Food', type='expense', amount=50, date=None):
        if date is None:
            date = datetime.date.today()
        return Transaction.objects.create(user=self.user, category=category, type=type, amount=amount, date=date)

    ### Unit Tests ###

    def test_category_wise_expense_report_response_format(self):
        url = reverse('category-wise-expense-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

        if len(response.data) > 0:
            # Check each item in the response list has the correct keys
            first_item = response.data[0]
            self.assertIn('category', first_item)
            self.assertIn('total_expense', first_item)

    ### Integration Tests ###

    def test_category_wise_expense_report(self):
        # Create some sample transactions
        self.create_transaction(category='Food', type='expense', amount=50)
        self.create_transaction(category='Transport', type='expense', amount=30)
        self.create_transaction(category='Food', type='expense', amount=20)
        self.create_transaction(category='Others', type='expense', amount=10)

        url = reverse('category-wise-expense-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Three distinct categories (Food, Transport, Others)

        # Check the correctness of the data returned
        expected_data = [
            {'category': 'Food', 'total_expense': 70},
            {'category': 'Others', 'total_expense': 10},
            {'category': 'Transport', 'total_expense': 30}
        ]

        self.assertEqual(response.data, expected_data)
