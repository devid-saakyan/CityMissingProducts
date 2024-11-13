from django.contrib import admin
from . import models


@admin.register(models.Reason)
class ReasonAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(models.ManagerReason)
class ManagerReasonAdmin(admin.ModelAdmin):
    list_display = ('main_reason', 'name', 'fee')


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sap_code', 'name', 'category_id')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_sap_code')


@admin.register(models.ProductsReport)
class ProductReportAdmin(admin.ModelAdmin):
    list_display = ('sap_code', 'category_sap_code', 'main_reason', 'manager_reason')