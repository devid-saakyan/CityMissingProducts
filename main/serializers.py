from rest_framework import serializers
from .models import *


class ReasonSerializer(serializers.ModelSerializer):
    manager_reasons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reason
        fields = ['id', 'name', 'manager_reasons_count']


class ManagerReasonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerReason
        fields = ['id', 'name', 'fee', 'main_reason']


class ProductsReportSerializer(serializers.ModelSerializer):
    sap_code_name = serializers.CharField(write_only=True, required=False)
    category_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ProductsReport
        fields = ['sap_code', 'sap_code_name', 'category_sap_code', 'category_name',
                  'main_reason', 'count', 'quantity', 'unit_price', 'branch']