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
                  'comment', 'date', 'order_id']


class ProductsReportInsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsReport
        fields = ['id', 'sap_code', 'sap_code_name', 'category_sap_code', 'category_sap_code_name',
                  'main_reason', 'user_basket_count', 'stock_count', 'unit_price', 'branch', 'image', 'date', 'order_id', 'is_kilogram']


class ProductReportIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    comment = serializers.CharField(max_length=150)


class UserReviewSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(required=True)

    class Meta:
        model = UserReview
        fields = ['id', 'order_id', 'user_bonus', 'rate', 'comment', 'created_at', 'branch_name']
        read_only_fields = ['id', 'created_at', 'branch_name']

    def create(self, validated_data):
        branch_name = validated_data.pop('branch_name', None)
        if branch_name:
            branch, _ = Branch.objects.get_or_create(name=branch_name)
            validated_data['branch'] = branch
        else:
            validated_data['branch'] = None

        return super().create(validated_data)


class UpdateUserReviewCategorySerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    category_id = serializers.IntegerField()


class UpdateReportReasonSerializer(serializers.Serializer):
    report_id = serializers.IntegerField()
    reason_id = serializers.IntegerField()