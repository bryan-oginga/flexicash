# Generated by Django 5.1.2 on 2024-11-12 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loanmanagement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanproduct',
            name='name',
            field=models.CharField(choices=[('Business Loan', 'Business Loan'), ('Personal Loan', 'Personal Loan'), ('Emergency Loan', 'Emergency Loan')], max_length=20),
        ),
    ]