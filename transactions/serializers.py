from rest_framework import serializers
from .models import Transaction
from authentication.serializers import UserSerializer


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model
    """

    def validate(self, attrs):
        if attrs['type'] == 'expense' and attrs['amount'] > self.context['request'].user.balance:
            raise serializers.ValidationError('Expense amount is greater than balance')
        
        return attrs

    class Meta:
        model = Transaction
        fields = ('pk', 'amount', 'type', 'category', 'date')
        read_only_fields = ('pk', )
