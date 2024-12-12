from datetime import datetime
import threading
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from main.bot import send_review_to_telegram, send_report_to_telegram
from .serializers import *
from django.db.models import Q, Count, Sum
from dateutil.parser import isoparse
from django.db.models import Count
from rest_framework.exceptions import NotFound
from .models import ReviewsCategory
from django.db.models import Func, F
from django.db.models.functions import Cast
from django.db.models import DateField
from rest_framework.pagination import PageNumberPagination
import calendar


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


class StaffCategoryListView(generics.ListAPIView):
    serializer_class = StaffCategorySerializer

    def get(self, request, *args, **kwargs):
        queryset = StaffCategory.objects.all()
        serializer = self.get_serializer(queryset, many=True)

        return Response({'success': True,
                         'data': serializer.data})


class ManagerReasonsListView(generics.ListAPIView):
    serializer_class = ManagerReasonsSerializer
    #category_name = serializers.CharField(source='category.name', read_only=True)

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


class UpdateManagerReasonView(generics.UpdateAPIView):
    queryset = ManagerReason.objects.all()
    serializer_class = ManagerReasonsSerializer
    http_method_names = ['post']

    def get_object(self):
        id = self.kwargs.get('id')
        return ManagerReason.objects.get(id=id)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"success": False, "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)


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
        print(report.is_kilogram)
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
                  report.user_basket_count / 1000 if report.is_kilogram is True else report.user_basket_count,
                  report.stock_count / 1000 if report.is_kilogram is True else report.stock_count,
                  report.is_kilogram),
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
            if report.manager_reason is None:
                report.manager_reason = reason
                report.fee = reason.fee
                report.save()
                return Response({"success": True, "message": "reason updated successfully."},
                                status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "manager reason already existsa"},
                                status=status.HTTP_304_NOT_MODIFIED)
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
            queryset = queryset.filter(manager_reason__isnull=True)
        elif filter_value == '2':
            queryset = queryset.filter(manager_reason__isnull=False)

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
            queryset = queryset.filter(manager_reason__isnull=True)
        elif filter_value == '2':
            queryset = queryset.filter(manager_reason__isnull=False)

        def parse_date(date_str):
            if not date_str:
                return datetime.min
            formats = [
                "%m/%d/%Y %I:%M:%S %p",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            try:
                parsed_date = isoparse(date_str)
                return parsed_date.replace(tzinfo=None)
            except ValueError:
                raise ValueError(f"Unknown date format: {date_str}")

        queryset = sorted(
            queryset,
            key=lambda obj: parse_date(obj.date),
            reverse=True
        )

        page = self.paginate_queryset(queryset)

        aggregation = ProductsReport.objects.filter(branch=branch_name).aggregate(
            resolved_true_count=Count('id', filter=Q(manager_reason__isnull=False)),
            resolved_false_count=Count('id', filter=Q(manager_reason__isnull=True))
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
            resolved_true_count=Count('id', filter=models.Q(manager_reason__isnull=False)),
            resolved_false_count=Count('id', filter=models.Q(manager_reason__isnull=True))
        ).order_by('branch')
        return Response(reports)


class ProductReportByBranchNameView(generics.GenericAPIView):
    serializer_class = ProductsReportSerializer

    def get(self, request, *args, **kwargs):
        branch_name = kwargs.get('branch_name')
        reports = ProductsReport.objects.filter(branch=branch_name).values('branch').annotate(
            resolved_true_count=Count('id', filter=models.Q(manager_reason__isnull=False)),
            resolved_false_count=Count('id', filter=models.Q(manager_reason__isnull=True))
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


@api_view(['GET'])
def product_report_view(request):
    try:
        reports = (
            ProductsReport.objects
            .values('branch', 'manager_reason__category__name', 'main_reason__name')
            .annotate(
                total_count=Count('id'),
                total_fee=Sum('fee')
            )
            .order_by('branch', 'manager_reason__category__name', 'main_reason__name')
        )

        data = [
            {
                "branch": report['branch'],
                "staff_category_name": report['manager_reason__category__name'],
                "main_reason": report['main_reason__name'],
                "count": report['total_count'],
                "sum_fee": report['total_fee']
            }
            for report in reports
        ]

        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def grouped_monthly_report_view(request):
    try:
        current_year = datetime.now().year
        main_reasons = Reason.objects.filter(name__in=["Out of stock", "Product Quality", "Expire Date"])
        data = []
        for month_id in range(1, 13):
            reports = ProductsReport.objects.all()
            month_total_count = 0
            month_total_fee = 0
            month_reasons_data = {reason.name: {"total_count": 0, "total_fee": 0} for reason in main_reasons}
            has_data = False
            for report in reports:
                if report.date:
                    try:
                        report_date = datetime.strptime(report.date, "%m/%d/%Y %I:%M:%S %p")
                        if report_date.month == month_id and report_date.year == current_year:
                            has_data = True
                            manager_reason = report.manager_reason
                            if manager_reason and manager_reason.main_reason in main_reasons:
                                reason_name = manager_reason.main_reason.name
                                fee = report.fee or 0
                                month_reasons_data[reason_name]["total_count"] += 1
                                month_reasons_data[reason_name]["total_fee"] += fee
                                month_total_count += 1
                                month_total_fee += fee
                    except ValueError:
                        continue

            if has_data:
                month_data = {
                    "month_year": f"{datetime(current_year, month_id, 1).strftime('%B')} {current_year}",
                    "out_of_stock": month_reasons_data["Out of stock"],
                    "product_quality": month_reasons_data["Product Quality"],
                    "expire_date": month_reasons_data["Expire Date"],
                    "total": {
                        "total_count": month_total_count,
                        "total_fee": month_total_fee
                    },
                    "status": 'Pending'
                }

                data.append(month_data)

        return Response({'success': True, 'data': data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_months(request):
    current_year = datetime.now().year
    reports = ProductsReport.objects.all()
    month_has_data = set()
    for report in reports:
        if report.date:
            try:
                report_date = datetime.strptime(report.date, "%m/%d/%Y %I:%M:%S %p")
                if report_date.year == current_year:
                    month_has_data.add(report_date.month)
            except ValueError:
                continue
    months = [
        {"id": month_id, "name": month_name, "exists": month_id in month_has_data}
        for month_id, month_name in enumerate(calendar.month_name)
        if month_name and month_id in month_has_data]

    return Response({
        "success": True,
        "data": months
    })