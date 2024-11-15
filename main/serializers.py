from rest_framework import serializers
from .models import *


class ReasonSerializer(serializers.ModelSerializer):
    manager_reasons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reason
        fields = ['id', 'name', 'manager_reasons_count']


class ManagerReasonsSerializer(serializers.ModelSerializer):
    used_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ManagerReason
        fields = ['id', 'name', 'fee', 'main_reason', 'active', 'used_count']


class DeleteManagerReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerReason
        fields = ['id']


class ProductsReportSerializer(serializers.ModelSerializer):
    main_reason = serializers.StringRelatedField()
    manager_reason = serializers.StringRelatedField()
    category_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ProductsReport
        fields = ['id', 'sap_code', 'sap_code_name', 'category_sap_code', 'category_sap_code_name', 'category_name',
                  'fee', 'manager_reason', 'main_reason', 'user_basket_count', 'stock_count', 'unit_price', 'branch', 'image', 'resolved',
                  'comment', 'date']


class ProductsReportInsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsReport
        fields = ['id', 'sap_code', 'sap_code_name', 'category_sap_code', 'category_sap_code_name',
                  'main_reason', 'user_basket_count', 'stock_count', 'unit_price', 'branch', 'image', 'date']


class ProductReportIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    comment = serializers.CharField(max_length=150)