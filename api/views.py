from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PayByLinkSerializer
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


@api_view(['POST'])
def create_report(request):
    pbl = request.data['pay_by_link']
    parsed_data = PayByLinkSerializer(data=pbl, many=True)
    if not parsed_data.is_valid():
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    reports = SortedList(key=lambda x:x["date"])
    for data in parsed_data.data:
        reports.add(prepare_single_report(data, 'pay_by_link', data['bank']))
    return Response(reports.__iter__())
