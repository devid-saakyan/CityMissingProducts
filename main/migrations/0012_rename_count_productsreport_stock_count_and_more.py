# Generated by Django 5.1.3 on 2024-11-14 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_productsreport_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productsreport',
            old_name='count',
            new_name='stock_count',
        ),
        migrations.RenameField(
            model_name='productsreport',
            old_name='quantity',
            new_name='user_basket_count',
        ),
        migrations.AddField(
            model_name='managerreason',
            name='active',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]