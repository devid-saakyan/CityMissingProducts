# Generated by Django 5.1.3 on 2024-12-02 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_staffcategory_managerreason_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='tabel_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
