# Generated by Django 5.1.3 on 2024-11-20 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_userreview_user_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='info',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
