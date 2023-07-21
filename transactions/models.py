from django.db import models


# Create your models here.
class Transaction(models.Model):
    """
    Model for transactions
    """
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey('authentication.User', related_name='translations', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.type} - {self.amount}"
