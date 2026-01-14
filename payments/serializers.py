from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    isPaid = serializers.BooleanField(source='is_paid')
    uniqueCode = serializers.CharField(source='unique_code')

    class Meta:
        model = Payment
        fields = ['isPaid', 'amount', 'uniqueCode', 'time']
