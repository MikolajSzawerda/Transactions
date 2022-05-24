from email.policy import default
from random import choices
from rest_framework import serializers
from rest_framework.serializers import Serializer
from .models import Customer


class ReportSerializer(Serializer):
    POSSIBLE_CURRENCIES = [
        ('PLN', 'PLN'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
        ('USD', 'USD')
    ]
    created_at = serializers.DateTimeField()
    currency = serializers.ChoiceField(choices=POSSIBLE_CURRENCIES)
    amount = serializers.IntegerField(min_value=0)
    description = serializers.CharField(max_length=200)


class PayByLinkSerializer(ReportSerializer):
    bank = serializers.CharField(max_length=200)


class DirectPaymentSerializer(ReportSerializer):
    iban = serializers.CharField(max_length=200)


class CardSerializer(ReportSerializer):
    cardholder_name = serializers.CharField(max_length=200)
    cardholder_surname = serializers.CharField(max_length=200)
    card_number = serializers.CharField(max_length=200)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'customer_data']


