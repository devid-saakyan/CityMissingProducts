from django.contrib import admin
from . import models


@admin.register(models.Reason)
class ReasonAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(models.StaffCategory)
class StaffCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )



@admin.register(models.ManagerReason)
class ManagerReasonAdmin(admin.ModelAdmin):
    list_display = ('main_reason', 'name', 'fee', 'category')


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sap_code', 'name', 'category_id')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_sap_code')


@admin.register(models.ProductsReport)
class ProductReportAdmin(admin.ModelAdmin):
    list_display = ('sap_code', 'category_sap_code', 'main_reason', 'manager_reason')


@admin.register(models.ReviewsCategory)
class ReviewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(models.UserReview)
class UserReviewAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'rate', 'comment')


@admin.register(models.Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(models.TelegramUserStatus)
class TelegramUserStatusAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(models.TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'status', 'branch', 'info', 'tabel_id', )


@admin.register(models.MonthlyReport)
class MonthReportAdmin(admin.ModelAdmin):
    list_display = ('month_year', 'total', 'status', )