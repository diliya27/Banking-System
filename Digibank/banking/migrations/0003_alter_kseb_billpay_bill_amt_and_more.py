# Generated by Django 5.1.5 on 2025-02-14 08:52

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0002_alter_deposittransaction_user_kseb_billpay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kseb_billpay',
            name='bill_amt',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='kseb_billpay',
            name='bill_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='kseb_billpay',
            name='consumer_number',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='kseb_billpay',
            name='mode_of_payment',
            field=models.CharField(blank=True, choices=[('UPI', 'UPI'), ('Net Banking', 'Net Banking'), ('Debit Card', 'Debit Card'), ('Credit Card', 'Credit Card')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='kseb_billpay',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')], default='Pending', max_length=15),
        ),
        migrations.AlterField(
            model_name='kseb_billpay',
            name='transaction_id',
            field=models.CharField(default=uuid.uuid4, max_length=50, unique=True),
        ),
    ]
