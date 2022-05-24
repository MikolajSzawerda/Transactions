from rest_framework import status
from django.urls import reverse
from .utils import json_correct_data, request_proccessed, apiclient
import pytest


@pytest.mark.parametrize('report_type', ['pay_by_link', 'dp' , 'card'])
def test_reporting_pay_by_link(apiclient, report_type):
    url = reverse('report')
    pbl_data = json_correct_data()[report_type]
    response = apiclient.post(url, {
        report_type: pbl_data
    }, format="json")
    assert response.status_code == status.HTTP_200_OK
    correct_response = request_proccessed(report_type)
    assert response.json() == correct_response


@pytest.mark.parametrize('report_type', ['pay_by_link', 'dp', 'card'])
def test_reporting_pay_by_link_lack_of_field(apiclient, report_type):
    url = reverse('report')
    pbl_data = json_correct_data()[report_type]
    keys = list(pbl_data[0].keys())
    for key in keys:
        for d in pbl_data:
            d.pop(key)
        response = apiclient.post(url, {
            report_type: pbl_data
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_example_request(apiclient):
    url = reverse('report')
    pbl_data = json_correct_data('example_request.json')
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    correct_response = request_proccessed('response')
    assert response.json() == correct_response


def test_distant_date_request(apiclient):
    url = reverse('report')
    pbl_data = json_correct_data('distant_data.json')
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    correct_response = request_proccessed('distant_data_response')
    assert response.json() == correct_response


def test_big_request(apiclient):
    url = reverse('report')
    pbl_data = json_correct_data('big_request.json')
    response = apiclient.post(url, pbl_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    correct_response = request_proccessed('big_response')
    assert response.json() == correct_response
