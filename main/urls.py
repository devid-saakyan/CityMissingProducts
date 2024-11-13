from django.urls import path
from .views import *


urlpatterns = [
    path('reasons', ReasonListView.as_view(), name='reason-list'),
    path('ManagerReasons/<int:reason_id>', ManagerReasonsListView.as_view(), name='manager-reason-list'),
    path('ManagerReasons/add', PostManagerReason.as_view(), name='manager-reasons-create'),
    path('ProductReport/add', ProductReportCreateView.as_view(), name='ProductReport'),
    path('ProductReport', ProductReportView.as_view(), name='ProductReport'),
    path('BranchReport', ProductReportGroupedByBranchView.as_view(), name='BranchReport'),
]
