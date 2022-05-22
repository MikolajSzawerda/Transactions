from urllib import response
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
import os
import json

def json_correct_data():
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'data.json')
    with open(file_path, 'r') as fh:
        data = json.load(fh)
    return data

def pay_by_link_proccesed():
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'pay_by_link.json')
    with open(file_path, 'r') as fh:
        data = json.load(fh)
    return data

class ReportAPITest(APITestCase):

    def test_always_pass(self):
        assert True

    def test_reporting_pay_by_link(self):
        url = reverse('report')
        pbl_data = json_correct_data()['pay_by_link']
        response = self.client.post(url, {
            'pay_by_link': pbl_data
        }, format="json")
        assert response.status_code == status.HTTP_200_OK
        correct_response = pay_by_link_proccesed()
        assert response.json() == correct_response

