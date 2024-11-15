# Generated by Django 5.1.2 on 2024-11-15 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lipanampesa', '0009_alter_loanmpesatransaction_amount_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loanmpesatransaction',
            options={'managed': True, 'verbose_name': 'Mpesa Payment', 'verbose_name_plural': 'Mpesa Payments'},
        ),
        migrations.AlterField(
            model_name='loanmpesatransaction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='loanmpesatransaction',
            name='email',
            field=models.EmailField(default='1', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='loanmpesatransaction',
            name='phone_number',
            field=models.CharField(blank=True, default='1', max_length=20, unique=True),
            preserve_default=False,
        ),
        migrations.AlterModelTable(
            name='loanmpesatransaction',
            table='',
        ),
    ]
