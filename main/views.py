from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Reason
from .serializers import *
from django.db.models import Count, Q
from django.db.models import Count
from django.utils.dateparse import parse_date
from rest_framework.exceptions import NotFound



class ReasonListView(generics.ListAPIView):
    serializer_class = ReasonSerializer

    def get(self, request, *args, **kwargs):
        queryset = Reason.objects.annotate(manager_reasons_count=Count('managerreason'))
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })


class ManagerReasonsListView(generics.ListAPIView):
    serializer_class = ManagerReasonsSerializer

    def get_queryset(self):
        print(self.kwargs)
        reason_id = self.kwargs.get('reason_id')
        if not reason_id:
            raise NotFound("reason_id parameter is required.")

        return ManagerReason.objects.filter(main_reason=reason_id)


class PostManagerReason(generics.CreateAPIView):
    queryset = ManagerReason.objects.all()
    serializer_class = ManagerReasonsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'success': False, 'errors': e.detail})


class DeleteManagerReason(generics.DestroyAPIView):
    serializer_class = DeleteManagerReasonSerializer
    queryset = ManagerReason.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': True})


class ProductReportCreateView(generics.CreateAPIView):
    queryset = ProductsReport.objects.all()
    serializer_class = ProductsReportSerializer

    def create(self, request, *args, **kwargs):
        sap_code = request.data.get('sap_code')
        category_sap_code = request.data.get('category_sap_code')
        sap_code_name = request.data.get('sap_code_name')
        category_name = request.data.get('category_name')

        product, _ = Product.objects.get_or_create(
            sap_code=sap_code,
            defaults={'name': sap_code_name}
        )
        category, _ = Category.objects.get_or_create(
            category_sap_code=category_sap_code,
            defaults={'name': category_name}
        )
        data = request.data.copy()
        data['sap_code'] = product.id
        data['category_sap_code'] = category.id
        data.pop('sap_code_name', None)
        data.pop('category_name', None)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ProductReportView(generics.ListAPIView):
    queryset = ProductsReport.objects.all()
    serializer_class = ProductsReportSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(serializer)
        return Response({'success': True,
                         'data': serializer.data})


class ProductReportByBranchView(generics.ListAPIView):
    serializer_class = ProductsReportSerializer

    def get_queryset(self):
        branch_name = self.kwargs.get('branch_name')
        queryset = ProductsReport.objects.filter(branch=branch_name)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})


class CombinedProductReportByBranchView(generics.GenericAPIView):
    serializer_class = ProductsReportSerializer

    def get(self, request, *args, **kwargs):
        branch_name = self.kwargs.get('branch_name')

        product_reports = ProductsReport.objects.filter(branch=branch_name)
        serializer = self.get_serializer(product_reports, many=True)

        aggregation = ProductsReport.objects.filter(branch=branch_name).aggregate(
            resolved_true_count=Count('id', filter=Q(resolved=True)),
            resolved_false_count=Count('id', filter=Q(resolved=False))
        )

        response_data = {
            'product_reports': serializer.data,
            'aggregation': {
                "resolved_true_count": aggregation["resolved_true_count"],
                "resolved_false_count": aggregation["resolved_false_count"]
            }
        }

        return Response({'success': True, 'data': response_data})


class ProductReportGroupedByBranchView(generics.GenericAPIView):
    serializer_class = ProductsReportSerializer
    def get(self, request):
        reports = ProductsReport.objects.values('branch').annotate(
            resolved_true_count=Count('id', filter=models.Q(resolved=True)),
            resolved_false_count=Count('id', filter=models.Q(resolved=False))
        ).order_by('branch')
        return Response(reports)


class ProductReportByBranchNameView(generics.GenericAPIView):
    serializer_class = ProductsReportSerializer

    def get(self, request, *args, **kwargs):
        branch_name = kwargs.get('branch_name')
        reports = ProductsReport.objects.filter(branch=branch_name).values('branch').annotate(
            resolved_true_count=Count('id', filter=Q(resolved=True)),
            resolved_false_count=Count('id', filter=Q(resolved=False))
        )
        return Response(reports)


class ProductReportUpdateByIdView(generics.GenericAPIView):
    serializer_class = ProductReportIdSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['id']
        comment = serializer.validated_data['comment']
        try:
            instance = ProductsReport.objects.get(id=product_id)
        except ProductsReport.DoesNotExist:
            return Response({"success": False, "error": "Product report not found"}, status=status.HTTP_404_NOT_FOUND)
        instance.fee = 0
        instance.resolved = True
        instance.comment = comment
        instance.save()

        return Response({"success": True, "message": "Product report updated successfully"}, status=status.HTTP_200_OK)
