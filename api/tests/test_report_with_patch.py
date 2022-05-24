from secrets import choice
from rest_framework import status
from django.urls import reverse
from .utils import json_correct_data, request_proccessed, apiclient, perform_patched_call
import pytest
from unittest.mock import patch
import json
import string


@patch("api.utils.perform_api_call", perform_patched_call)
def test_big_request(apiclient):
    url = reverse('report')
    pbl_data = json_correct_data('big_data.json')
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    correct_response = request_proccessed('big_data_response')
    for report in response.json():
        assert report in correct_response


@patch("api.utils.perform_api_call", perform_patched_call)
def test_date_validation(apiclient):
    url = reverse('report')
    pbl_data = json_correct_data('example_request.json')
    date = pbl_data['pay_by_link'][0]['created_at'].split('T')
    date = '2021-02-31'+'T'+date[1]
    pbl_data['pay_by_link'][0]['created_at'] = date
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("api.utils.perform_api_call", perform_patched_call)
def test_amount_validation(apiclient):
    url = reverse('report')
    pbl_data = json_correct_data('example_request.json')
    pbl_data['pay_by_link'][0]['amount'] = -3000
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def generate_faulty_currency():
    CURRENCY = set(["EUR", "USD", "GBP", "PLN"])
    curr = 'PLN'
    while curr in CURRENCY:
        curr = ''.join([choice(string.ascii_uppercase) for _ in range(3)])
    return curr


@patch("api.utils.perform_api_call", perform_patched_call)
def test_currency_validation(apiclient):
    url = reverse('report')
    pbl_data = json_correct_data('example_request.json')
    pbl_data['pay_by_link'][0]['currency'] = generate_faulty_currency()
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
