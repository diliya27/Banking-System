# Generated by Django 5.1.5 on 2025-02-18 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0007_alter_waterbillpayment_amount_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposittransaction',
            name='order_id',
            field=models.CharField(max_length=500, unique=True),
        ),
    ]
