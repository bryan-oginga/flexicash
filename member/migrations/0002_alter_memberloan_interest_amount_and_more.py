# Generated by Django 5.1.2 on 2024-11-09 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberloan',
            name='interest_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='memberloan',
            name='interest_rate',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='memberloan',
            name='loan_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='memberloan',
            name='total_repayment',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
