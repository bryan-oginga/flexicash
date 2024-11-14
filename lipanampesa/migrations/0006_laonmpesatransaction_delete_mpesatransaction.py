# Generated by Django 5.1.2 on 2024-11-14 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lipanampesa', '0005_mpesatransaction_invoice_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaonMpesaTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_id', models.CharField(max_length=100, unique=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('narrative', models.CharField(max_length=255)),
                ('state', models.CharField(default='PENDING', max_length=20)),
            ],
        ),
        migrations.DeleteModel(
            name='MpesaTransaction',
        ),
    ]
