from rest_framework import status
from django.urls import reverse
from .utils import json_correct_data, request_proccessed, apiclient, perform_patched_call
import pytest
from unittest.mock import patch
import json
import string


@patch("api.utils.perform_api_call", perform_patched_call)
@pytest.mark.django_db
def test_big_request(apiclient):
    url = reverse('customer-report')
    pbl_data = json_correct_data('big_data.json')
    pbl_data['customer_id'] = 4
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@patch("api.utils.perform_api_call", perform_patched_call)
@pytest.mark.django_db
def test_retrieving_unknown_user(apiclient):
    url = reverse('customer-report-id', kwargs={'customer_id': 1234})
    response = apiclient.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@patch("api.utils.perform_api_call", perform_patched_call)
@pytest.mark.django_db
def test_customer_update(apiclient):
    url = reverse('customer-report')
    pbl_data = json_correct_data('big_data.json')
    pbl_data['customer_id'] = 4
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    pbl_data = json_correct_data('example_request.json')
    pbl_data['customer_id'] = 4
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    url = reverse('customer-report-id', kwargs={'customer_id': 4})
    response = apiclient.get(url)
    correct_response = json_correct_data('response.json')
    assert response.json()==correct_response