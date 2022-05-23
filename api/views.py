from asyncio import futures
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PayByLinkSerializer, DirectPaymentSerializer, CardSerializer
from sortedcontainers import SortedList
import time
from functools import lru_cache
import requests
from math import floor
import concurrent.futures


class InvalidPaymentData(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

URLS = {
    'date_interval':'http://api.nbp.pl/api/exchangerates/rates/c/{}/{}/{}'
}

@lru_cache(maxsize=120)
def perform_api_call(currency: str, date):
    days_backup = (datetime.strptime(date, "%Y-%m-%d")-timedelta(3))
    formated_date = days_backup.strftime("%Y-%m-%d")
    url = URLS['date_interval'].format(currency.lower(), formated_date, date)
    response = requests.get(url)
    # print(response)
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        rate = data['rates'][-1]['bid']
        return rate
    days_backup = (days_backup-timedelta(3))
    url = URLS['date_interval'].format(currency.lower(), days_backup.strftime("%Y-%m-%d"), formated_date)
    response = requests.get(url)
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        rate = data['rates'][-1]['bid']
        return rate
    return 1

def convert_to_pln(data):
    currency = data['currency']
    amount = data['amount']
    if data['currency'] == 'PLN':
        return amount
    ymd_date = data['created_at'].split('T')[0]
    rate = perform_api_call(currency, ymd_date)
    return floor(rate*amount)


def prepare_single_report(data, type, payment_mean):
    amount_in_pln = convert_to_pln(data)
    return {
            "date": data['created_at'],
            "type": type,
            "payment_mean": payment_mean,
            "description": data['description'],
            "currency": data['currency'],
            "amount": data['amount'],
            "amount_in_pln": amount_in_pln
        }


def prepare_card_data(data):
    number = data['card_number']
    num = len(number)//2
    stars = '*'*num
    number = number[:num//2]+stars+number[3*num//2:]
    return ' '.join([data['cardholder_name'], data['cardholder_surname'], number])


def validate_data(payment_data, serializer):
    if payment_data:
        parsed_data = serializer(data=payment_data, many=True)
        if not parsed_data.is_valid():
            raise InvalidPaymentData()
        return parsed_data.data
    return list()


METHODS = {
    'pay_by_link': {
        'serializer': PayByLinkSerializer,
        'mean': lambda x: x['bank']
    },
    'dp': {
        'serializer': DirectPaymentSerializer,
        'mean': lambda x: x['iban']
    },
    'card': {
        'serializer': CardSerializer,
        'mean': prepare_card_data
    }
}
"""
with concurrent.futures.ThreadPoolExecutor() as exec:
        proccesed_repos = [exec.submit(prepare_repository_data, repo, header) for repo in data]
        for repo in concurrent.futures.as_completed(proccesed_repos):
            repo_data = repo.result()
            agreggate_language(repo_data['languages'], agregator)
            repos.append(repo_data)
"""

@api_view(['POST'])
def create_report(request):
    reports = SortedList(key=lambda x: x["date"])
    try:
        for key in request.data.keys():
            behaviour = METHODS[key]
            pbl = request.data.get(key, None)
            parsed_data = validate_data(pbl, behaviour['serializer'])
            with concurrent.futures.ThreadPoolExecutor() as exec:
                proccesed_reports = [
                    exec.submit(
                        prepare_single_report, data, key,
                        behaviour['mean'](data)) for data in parsed_data
                    ]
            for data in concurrent.futures.as_completed(proccesed_reports):
                reports.add(data.result())
    except InvalidPaymentData:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    return Response(reports.__iter__())
