# Generated by Django 5.1.2 on 2024-12-07 12:10

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlexiCashMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('pin', models.CharField(max_length=10)),
                ('member_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('membership_number', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('loan_limit', models.DecimalField(decimal_places=2, default=Decimal('500.00'), max_digits=10)),
                ('credit_score', models.IntegerField(default=50)),
            ],
            options={
                'verbose_name': 'FlexiCash Member',
                'verbose_name_plural': 'FlexiCash Members',
            },
        ),
    ]