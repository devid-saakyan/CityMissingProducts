# Generated by Django 5.1.3 on 2024-11-14 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_productsreport_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsreport',
            name='image',
            field=models.CharField(default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTpZCt7LU6IqViTi4j0Y-SkMRytp2EWCldug&s', max_length=1000),
            preserve_default=False,
        ),
    ]
