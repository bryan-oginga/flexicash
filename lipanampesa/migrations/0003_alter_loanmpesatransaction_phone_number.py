# Generated by Django 5.1.2 on 2024-11-21 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lipanampesa', '0002_loanmpesatransaction_delete_mpesatransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanmpesatransaction',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
