# Generated by Django 5.1.3 on 2024-11-13 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_productsreport_resolved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsreport',
            name='category_sap_code',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productsreport',
            name='sap_code',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
    ]
