from django.db import models

# Create your models here.
class Customer(models.Model):
    customer_id = models.BigIntegerField(unique=True)
    customer_data = models.TextField()