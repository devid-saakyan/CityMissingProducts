from django.db import models


class Reason(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class StaffCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ManagerReason(models.Model):
    main_reason = models.ForeignKey(Reason, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, unique=False)
    fee = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(null=True, blank=True)
    category = models.ForeignKey(StaffCategory, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    category_sap_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    sap_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    category_id = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class ProductsReport(models.Model):
    sap_code = models.CharField(max_length=20)
    sap_code_name = models.CharField(max_length=30)
    category_sap_code = models.CharField(max_length=20)
    category_sap_code_name = models.CharField(max_length=40)
    main_reason = models.ForeignKey('Reason', on_delete=models.SET_NULL, null=True, blank=True)
    manager_reason = models.ForeignKey('ManagerReason', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='product_reports')
    fee = models.IntegerField(null=True, blank=True)
    user_basket_count = models.IntegerField()
    stock_count = models.IntegerField()
    unit_price = models.FloatField()
    branch = models.CharField(max_length=100)
    resolved = models.BooleanField(default=False)
    image = models.CharField(max_length=1000)
    comment = models.CharField(max_length=150, null=True, blank=True)
    date = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.IntegerField(null=True, blank=True)
    is_kilogram = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"Report for Product {self.sap_code} in Category {self.category_sap_code}"


class ReviewsCategory(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class ReviewsCategoryAnswer(models.Model):
    main_category = models.ForeignKey(ReviewsCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name



class Branch(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class UserReview(models.Model):
    order_id = models.CharField(max_length=50, verbose_name="Order ID")
    user_bonus = models.CharField(max_length=100)
    rate = models.PositiveSmallIntegerField(verbose_name="Rating (1-5)")
    order_date = models.CharField(max_length=100, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,)
    comment = models.TextField(verbose_name="Complaint Comment")
    category = models.ForeignKey(ReviewsCategory, on_delete=models.SET_NULL, null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    category_answer = models.ForeignKey(ReviewsCategoryAnswer, on_delete=models.SET_NULL, null=True, blank=True)
    category_comment = models.CharField(max_length=150, null=True, blank=True)
    category_answer_comment = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Complaint for Order {self.order_id} (Rate: {self.rate})"


class TelegramUserStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TelegramUser(models.Model):
    user_id = models.CharField(max_length=50, unique=True)
    status = models.ForeignKey(TelegramUserStatus, on_delete=models.SET_NULL, null=True, blank=True, )
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, )
    info = models.CharField(max_length=200, null=True, blank=True)
    tabel_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user_id


class MonthlyReport(models.Model):
    id = models.AutoField(primary_key=True)
    month_year = models.CharField(max_length=50)
    out_of_stock = models.JSONField()
    product_quality = models.JSONField()
    expire_date = models.JSONField()
    total = models.JSONField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return self.month_year