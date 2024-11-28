# Generated by Django 5.1.2 on 2024-11-28 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesaexpress', '0002_alter_mpesatransaction_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mpesatransaction',
            name='callback_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='mpesatransaction',
            name='checkout_request_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='mpesatransaction',
            name='merchant_request_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='mpesatransaction',
            name='mpesa_receipt_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='mpesatransaction',
            name='result_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mpesatransaction',
            name='result_desc',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='mpesatransaction',
            name='status',
            field=models.CharField(blank=True, default='Pending', max_length=20, null=True),
        ),
    ]