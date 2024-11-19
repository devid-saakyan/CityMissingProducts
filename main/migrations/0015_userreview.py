# Generated by Django 5.1.3 on 2024-11-15 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_managerreason_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=50, verbose_name='Order ID')),
                ('rate', models.PositiveSmallIntegerField(verbose_name='Rating (1-5)')),
                ('comment', models.TextField(verbose_name='Complaint Comment')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
            ],
        ),
    ]
