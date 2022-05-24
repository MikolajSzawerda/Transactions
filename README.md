# Transactions

# Assumptions

My task was to prepare a server application which transforms given payment data in json form into a response in a given specification.

A sub-task was to integrate the application with an external api. When sending requests to the external nbp api, a lru cache is used, due to the high probability of requesting the same dates in one request. In addition, one of the difficulties was the unsatisfactory response of the api in the case of a day being a weekend or a holiday. I solved the problem by asking in each query for data from three days back, along with if the response is still 404, I send another(last) request for next 3 days back.
Since the api documentation does not specify the time in which the dates are given, I assumed that they are given in UTC time

# Endpoints

```POST api/report``` - returns response in given format

```POST api/customer-report``` - returns the same data as ```api/report```, but also require 'customer_id' in the body(allows to update or create customer with given id)

```GET api/customer-report/<int:customer_id>``` - retireves data for given customer

### venv setup

```python3 -m venv venv```

```source venv/bin/activate```

### Installation of the required packages

```pip install -r requirements.txt```

### Django configuration

```python3 manage.py migrate```

```python3 manage.py makemigrations```

### Starting the server

```python3 manage.py runserver```

The server will be run at localhost:8000
