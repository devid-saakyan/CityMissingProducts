from django.urls import path
from .views import *


urlpatterns = [
    path('reasons', ReasonListView.as_view(), name='reason-list'),
    path('ManagerReasons/<int:reason_id>', ManagerReasonsListView.as_view(), name='manager-reason-list'),
    path('ManagerReasons/delete/<int:id>', DeleteManagerReason.as_view(), name='delete-manager-reason'),
    path('ManagerReasons/deactivate/<int:id>/', DeactivateManagerReason.as_view(), name='deactivate-manager-reason'),
    path('ManagerReasons/activate/<int:id>/', ActivateManagerReason.as_view(), name='activate-manager-reason'),
    path('ManagerReasons/add', PostManagerReason.as_view(), name='manager-reasons-create'),
    path('ProductReport/add', ProductReportCreateView.as_view(), name='ProductReport'),
    path('UpdateProductReport', UpdateUserReportReasonView.as_view(), name='UpdateProductReport'),
    path('ProductReport', ProductReportView.as_view(), name='ProductReport'),
    path('ProductReport/<str:branch_name>', CombinedProductReportByBranchView.as_view(), name='product-report-by-branch'),
    path('ProductReport/cancel/', ProductReportUpdateByIdView.as_view(), name='product-report-update'),
    path('BranchReport', ProductReportGroupedByBranchView.as_view(), name='BranchReport'),
    path('BranchReport/<str:branch_name>', ProductReportByBranchNameView.as_view(), name='ReportByBranch'),
    path('UserReview/add', UserReviewCreateView.as_view(), name='user-review-add'),
    path('UserReview/exists/ById/<str:order_id>', GetOrderRateStatusByOrderId.as_view(), name='user-review--by-order-id'),
    path('UserReview/exists/ByBonus/<str:user_bonus>', GetOrderRateStatusByBonus.as_view(), name='user-review-by-bonus'),
    path('UpdateReviewCategory', UpdateUserReviewCategoryView.as_view(), name='update-review-category'),
]
