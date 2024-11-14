from django.db import models


class Reason(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ManagerReason(models.Model):
    main_reason = models.ForeignKey(Reason, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)
    fee = models.IntegerField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    category_sap_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    sap_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    category_id = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class ProductsReport(models.Model):
    sap_code = models.CharField(max_length=20)
    sap_code_name = models.CharField(max_length=30)
    category_sap_code = models.CharField(max_length=20)
    category_sap_code_name = models.CharField(max_length=40)
    main_reason = models.ForeignKey('Reason', on_delete=models.SET_NULL, null=True, blank=True)
    manager_reason = models.ForeignKey('ManagerReason', on_delete=models.SET_NULL, null=True, blank=True)
    fee = models.IntegerField(null=True, blank=True)
    count = models.IntegerField()
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    branch = models.CharField(max_length=100)
    resolved = models.BooleanField(default=False)
    image = models.CharField(max_length=1000)
    comment = models.CharField(max_length=150, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report for Product {self.sap_code} in Category {self.category_sap_code}"