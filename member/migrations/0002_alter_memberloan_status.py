# Generated by Django 5.1.2 on 2024-11-09 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberloan',
            name='status',
            field=models.CharField(default='PENDING', max_length=20),
        ),
    ]
