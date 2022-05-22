from rest_framework import serializers
from rest_framework.serializers import Serializer


class ReportSerializer(Serializer):
    created_at = serializers.DateTimeField()
    currency = serializers.CharField(max_length=200)
    amount = serializers.IntegerField()
    description = serializers.CharField(max_length=200)


class PayByLinkSerializer(ReportSerializer):
    bank = serializers.CharField(max_length=200)


class DirectPaymentSerializer(ReportSerializer):
    iban = serializers.CharField(max_length=200)


class CardSerializer(ReportSerializer):
    cardholder_name = serializers.CharField(max_length=200)
    cardholder_surname = serializers.CharField(max_length=200)
    card_number = serializers.CharField(max_length=200)




