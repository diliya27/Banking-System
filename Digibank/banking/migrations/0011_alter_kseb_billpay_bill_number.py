# Generated by Django 5.1.5 on 2025-02-18 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0010_alter_kseb_billpay_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kseb_billpay',
            name='bill_number',
            field=models.CharField(max_length=20),
        ),
    ]
