# Generated by Django 5.1.3 on 2025-01-24 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_monthlyreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreview',
            name='rate_date',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
