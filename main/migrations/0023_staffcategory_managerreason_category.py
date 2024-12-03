# Generated by Django 5.1.3 on 2024-12-02 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_productsreport_is_kilogram_productsreport_order_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='managerreason',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.staffcategory'),
        ),
    ]