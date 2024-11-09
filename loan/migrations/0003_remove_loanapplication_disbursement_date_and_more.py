# Generated by Django 5.1.2 on 2024-11-09 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loanapplication',
            name='disbursement_date',
        ),
        migrations.AlterField(
            model_name='loanapplication',
            name='loan_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REPAID', 'Repaid'), ('DEFAULTED', 'Defaulted'), ('DISBURSED', 'Disbursed')], default='PENDING', max_length=10),
        ),
    ]
