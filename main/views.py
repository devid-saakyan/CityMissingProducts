import threading
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from main.bot import send_review_to_telegram, send_report_to_telegram
from .serializers import *
from django.db.models import Q
from django.db.models import Count
from rest_framework.exceptions import NotFound
from .models import ReviewsCategory
from django.db.models import Func, F
from django.db.models.functions import Cast
from django.db.models import DateField
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'count'
    page_size = 10
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'list': data,
            'ItemCount': self.page.paginator.count,
            'PageCount': self.page.paginator.num_pages
        })


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
        reason_id = self.kwargs.get('reason_id')
        if not reason_id:
            raise NotFound("reason_id parameter is required.")

        queryset = ManagerReason.objects.filter(main_reason=reason_id).annotate(
            used_count=Count('product_reports')
        )

        return queryset


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


class ActivateManagerReason(generics.UpdateAPIView):
    serializer_class = DeleteManagerReasonSerializer
    queryset = ManagerReason.objects.all()
    lookup_field = 'id'

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = True
        instance.save(update_fields=['active'])  # Сохраняем только поле active
        return Response({'success': True})


class DeactivateManagerReason(generics.UpdateAPIView):
    serializer_class = DeleteManagerReasonSerializer
    queryset = ManagerReason.objects.all()
    lookup_field = 'id'

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = False
        instance.save(update_fields=['active'])
        return Response({'success': True})


class ProductReportCreateView(generics.CreateAPIView):
    queryset = ProductsReport.objects.all()
    serializer_class = ProductsReportInsertSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'image', openapi.IN_FORM, type=openapi.TYPE_FILE, description="Image file"
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        sap_code = request.data.get('sap_code')
        category_sap_code = request.data.get('category_sap_code')
        sap_code_name = request.data.get('sap_code_name')
        category_name = request.data.get('category_sap_code_name')

        product, _ = Product.objects.get_or_create(
            sap_code=sap_code,
            defaults={'name': sap_code_name}
        )
        category, _ = Category.objects.get_or_create(
            category_sap_code=category_sap_code,
            defaults={'name': category_name}
        )
        data = request.data.copy()
        data['sap_code'] = product.sap_code
        data['category_sap_code'] = category.category_sap_code
        data['sap_code_name'] = sap_code_name
        data['category_sap_code_name'] = category_name
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        reasons = list(ManagerReason.objects.filter(main_reason=data['main_reason']).values('id', 'name'))
        print(reasons)
        self.perform_create(serializer)
        report = serializer.save()
        print(report.main_reason)
        threading.Thread(
            target=send_report_to_telegram,
            args=(report.sap_code_name,
                  report.sap_code,
                  report.unit_price,
                  report.id,
                  report.image,
                  reasons,
                  report.branch,
                  report.main_reason,
                  report.user_basket_count,
                  report.stock_count),
            daemon=True
        ).start()
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class UpdateUserReportReasonView(views.APIView):
    @swagger_auto_schema(
        request_body=UpdateReportReasonSerializer,
        responses={
            200: "reason updated successfully.",
            400: "Invalid report or reason ID."
        }
    )
    def post(self, request, *args, **kwargs):
        report_id = request.data.get("report_id")
        reason_id = request.data.get("reason_id")
        try:
            report = ProductsReport.objects.get(id=report_id)
            reason = ManagerReason.objects.get(id=reason_id)
            report.manager_reason = reason
            report.fee = reason.fee
            report.resolved = True
            report.save()
            return Response({"success": True, "message": "reason updated successfully."},
                            status=status.HTTP_200_OK)
        except (ProductsReport.DoesNotExist, ManagerReason.DoesNotExist):
            return Response({"success": False, "message": "Invalid report or reason ID."},
                            status=status.HTTP_400_BAD_REQUEST)


class ProductReportView(generics.ListAPIView):
    serializer_class = ProductsReportSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        filter_value = self.request.query_params.get('filter')
        queryset = ProductsReport.objects.annotate(
            date_as_date=Cast('date', output_field=DateField())
        ).order_by('-date_as_date')

        if filter_value == '1':
            queryset = queryset.filter(resolved=False)
        elif filter_value == '2':
            queryset = queryset.filter(resolved=True)

        return queryset


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


class CombinedProductReportByBranchView(generics.ListAPIView):
    serializer_class = ProductsReportSerializer
    pagination_class = CustomPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('filter', openapi.IN_QUERY, description="0: All, 1: Resolved=False, 2: Resolved=True",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('branch_name', openapi.IN_PATH, description="Branch Name", type=openapi.TYPE_STRING),
        ],
        operation_description="Retrieve product reports by branch with optional filtering and pagination",
        responses={200: "List of product reports with resolved and unresolved counts."}
    )
    def get(self, request, *args, **kwargs):
        branch_name = self.kwargs.get('branch_name')
        filter_value = self.request.query_params.get('filter')

        queryset = ProductsReport.objects.filter(branch=branch_name)
        if filter_value == '1':
            queryset = queryset.filter(resolved=True)
        elif filter_value == '2':
            queryset = queryset.filter(resolved=False)

        page = self.paginate_queryset(queryset)

        aggregation = ProductsReport.objects.filter(branch=branch_name).aggregate(
            resolved_true_count=Count('id', filter=Q(resolved=True)),
            resolved_false_count=Count('id', filter=Q(resolved=False))
        )

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data.update({
                "aggregation": {
                    "resolved_true_count": aggregation["resolved_true_count"],
                    "resolved_false_count": aggregation["resolved_false_count"]
                }
            })
            return paginated_response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            "aggregation": {
                "resolved_true_count": aggregation["resolved_true_count"],
                "resolved_false_count": aggregation["resolved_false_count"]
            }
        })


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


class UserReviewCreateView(generics.CreateAPIView):
    queryset = UserReview.objects.all()
    serializer_class = UserReviewSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        review = serializer.save()
        categories = list(ReviewsCategory.objects.values("id", "name"))

        branch_name = review.branch.name if review.branch else "Филиал не указан"

        threading.Thread(
            target=send_review_to_telegram,
            args=(review.order_id, review.rate, review.comment, review.id, categories, branch_name),
            daemon=True
        ).start()

        return Response({'success': True, 'data': serializer.data})


class UpdateUserReviewCategoryView(views.APIView):
    @swagger_auto_schema(
        request_body=UpdateUserReviewCategorySerializer,
        responses={
            200: "Category updated successfully.",
            400: "Invalid review or category ID."
        }
    )
    def post(self, request, *args, **kwargs):
        review_id = request.data.get("review_id")
        category_id = request.data.get("category_id")
        try:
            review = UserReview.objects.get(id=review_id)
            category = ReviewsCategory.objects.get(id=category_id)
            review.category = category
            review.save()
            return Response({"success": True, "message": "Category updated successfully."}, status=status.HTTP_200_OK)
        except (UserReview.DoesNotExist, ReviewsCategory.DoesNotExist):
            return Response({"success": False, "message": "Invalid review or category ID."}, status=status.HTTP_400_BAD_REQUEST)


class GetOrderRateStatusByOrderId(generics.ListAPIView):
    serializer_class = UserReviewSerializer

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        reports = UserReview.objects.filter(order_id=order_id).values('order_id')
        if len(reports) == 0:
            return Response({"exists": False, "data": reports})
        else:
            return Response({"exists": True, "data": reports})


class GetOrderRateStatusByBonus(generics.ListAPIView):
    serializer_class = UserReviewSerializer

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('user_bonus')
        reports = UserReview.objects.filter(order_id=order_id).values('user_bonus')
        if len(reports) == 0:
            return Response({"exists": False, "data": reports})
        else:
            return Response({"exists": True, "data": reports})