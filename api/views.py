from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PayByLinkSerializer, DirectPaymentSerializer, CardSerializer
from functools import lru_cache
import requests
from math import floor
import concurrent.futures


class InvalidPaymentData(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UnsupportedDate(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


URLS = {
    'date_interval': 'http://api.nbp.pl/api/exchangerates/rates/c/{}/{}/{}'
}

DAYS_BACKUP = 3
API_CALL_RETRY = 2
ACCEPTED_STATUS = set((status.HTTP_200_OK, status.HTTP_404_NOT_FOUND))
DATE_FORMAT = "%Y-%m-%d"


@lru_cache(maxsize=128)
def perform_api_call(currency: str, date):
    num_of_tries = 0
    st = status.HTTP_200_OK
    end_date = date
    while num_of_tries < API_CALL_RETRY and st in ACCEPTED_STATUS:
        days_backup = (datetime.strptime(end_date, DATE_FORMAT) - timedelta(DAYS_BACKUP))
        start_date = days_backup.strftime(DATE_FORMAT)
        url = URLS['date_interval'].format(currency.lower(), start_date, end_date)
        response = requests.get(url)
        st = response.status_code
        if st == status.HTTP_200_OK:
            data = response.json()
            rate = data['rates'][-1]['bid']
            return rate
        end_date = start_date
        num_of_tries += 1
    raise UnsupportedDate


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


@api_view(['POST'])
def create_report(request):
    reports = list()
    try:
        for key in request.data.keys():
            behaviour = METHODS[key]
            data = request.data.get(key, None)
            parsed_data = validate_data(data, behaviour['serializer'])
            with concurrent.futures.ThreadPoolExecutor() as exec:
                proccesed_reports = [
                    exec.submit(
                        prepare_single_report, data, key,
                        behaviour['mean'](data)) for data in parsed_data
                    ]
            for data in concurrent.futures.as_completed(proccesed_reports):
                reports.append(data.result())
    except InvalidPaymentData:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    except UnsupportedDate:
        return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)
    return Response(sorted(reports, key=lambda x: x["date"]))
