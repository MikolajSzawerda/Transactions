from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PayByLinkSerializer, DirectPaymentSerializer, CardSerializer
from sortedcontainers import SortedList


def prepare_single_report(data, type, payment_mean):
    return {
            "date": data['created_at'],
            "type": type,
            "payment_mean": payment_mean,
            "description": data['description'],
            "currency": data['currency'],
            "amount": data['amount'],
            "amount_in_pln": data['amount']
        }


def prepare_card_data(name, surname, number):
    num = len(number)//2
    stars = '*'*num
    number = number[:num//2]+stars+number[3*num//2:]
    return ' '.join([name, surname, number])


@api_view(['POST'])
def create_report(request):
    pbl = request.data.get('pay_by_link', None)
    if pbl:
        parsed_data = PayByLinkSerializer(data=pbl, many=True)
        if not parsed_data.is_valid():
            return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
        reports = SortedList(key=lambda x:x["date"])
        for data in parsed_data.data:
            reports.add(prepare_single_report(data, 'pay_by_link', data['bank']))

    dp = request.data.get('dp', None)
    if dp:
        parsed_data = DirectPaymentSerializer(data=dp, many=True)
        if not parsed_data.is_valid():
            return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
        reports = SortedList(key=lambda x:x["date"])
        for data in parsed_data.data:
            reports.add(prepare_single_report(data, 'dp', data['iban']))

    card = request.data.get('card', None)
    if card:
        parsed_data = CardSerializer(data=card, many=True)
        if not parsed_data.is_valid():
            return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
        reports = SortedList(key=lambda x:x["date"])
        for data in parsed_data.data:
            name = data['cardholder_name']
            surname = data['cardholder_surname']
            number = data['card_number']
            reports.add(prepare_single_report(data, 'card', prepare_card_data(name, surname, number)))
    return Response(reports.__iter__())
