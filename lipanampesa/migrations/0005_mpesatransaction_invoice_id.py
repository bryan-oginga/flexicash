# Generated by Django 5.1.2 on 2024-11-13 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lipanampesa', '0004_remove_mpesatransaction_channel_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpesatransaction',
            name='invoice_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]