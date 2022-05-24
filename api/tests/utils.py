import os
import pytest
import json
from rest_framework.test import APIClient


def json_correct_data(filename='data_2.json'):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, filename)
    with open(file_path, 'r') as fh:
        data = json.load(fh)
    return data


def request_proccessed(file_name):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, f'{file_name}.json')
    with open(file_path, 'r') as fh:
        data = json.load(fh)
    return data


@pytest.fixture
def apiclient():
    return APIClient()


def perform_patched_call(currency: str, date):
    data = json_correct_data(f'fixtures/currency_{currency}.json')
    previous = data['rates'][0]
    for d in data['rates']:
        current_date = d['effectiveDate']
        if current_date == date:
            return d['bid']
        if current_date > date:
            return previous['bid']
        previous = d
