# Generated by Django 5.1.3 on 2024-11-14 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_productsreport_category_sap_code_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsreport',
            name='comment',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
