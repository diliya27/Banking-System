# Generated by Django 5.1.5 on 2025-02-21 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0015_alter_waterbillpayment_consumer_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='waterbillpayment',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
