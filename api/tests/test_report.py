from urllib import response
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
import os
import json
import pytest
# from parameterized import parameterized


def json_correct_data():
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'data.json')
    with open(file_path, 'r') as fh:
        data = json.load(fh)
    return data


def pay_by_link_proccesed(file_name):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, f'{file_name}.json')
    with open(file_path, 'r') as fh:
        data = json.load(fh)
    return data


@pytest.fixture
def apiclient():
    return APIClient()


@pytest.mark.parametrize('report_type', ['pay_by_link', 'dp' , 'card'])
def test_reporting_pay_by_link(apiclient, report_type):
    url = reverse('report')
    pbl_data = json_correct_data()[report_type]
    response = apiclient.post(url, {
        report_type: pbl_data
    }, format="json")
    assert response.status_code == status.HTTP_200_OK
    correct_response = pay_by_link_proccesed(report_type)
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


