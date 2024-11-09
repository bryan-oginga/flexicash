# Generated by Django 5.1.2 on 2024-11-09 05:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('loan', '0001_initial'),
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanapplication',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_applications', to='member.flexicashmember'),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='loan_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='loan_applications', to='loan.loantype'),
        ),
    ]
