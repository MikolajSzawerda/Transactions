from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
import json
from .utils import proccess_payment_mean, InvalidPaymentData, UnsupportedDate


@api_view(['POST'])
def create_report(request) -> Response:
    reports = list()
    try:
        for key in request.data.keys():
            proccess_payment_mean(key, request.data, reports)
    except InvalidPaymentData:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    except UnsupportedDate:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    return Response(sorted(reports, key=lambda x: x["date"]))


@api_view(['POST'])
def create_customer_report(request):
    reports = list()
    try:
        customer_id = request.data.pop('customer_id')
        for key in request.data.keys():
            proccess_payment_mean(key, request.data, reports)
        customer_instance, created = Customer.objects.update_or_create(customer_id=customer_id, defaults={
            'customer_data': json.dumps(reports)
        })
        st = status.HTTP_200_OK
        if created:
            st = status.HTTP_201_CREATED
    except InvalidPaymentData:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    except UnsupportedDate:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    return Response(sorted(reports, key=lambda x: x["date"]), status=st)


@api_view(['GET'])
def get_customer_report(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response("Invalid data!", status=status.HTTP_404_NOT_FOUND)
    return Response(sorted(json.loads(customer.customer_data), key=lambda x: x["date"]))