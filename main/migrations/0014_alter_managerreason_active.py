# Generated by Django 5.1.3 on 2024-11-14 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_alter_managerreason_fee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managerreason',
            name='active',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
