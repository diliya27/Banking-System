# Generated by Django 5.1.5 on 2025-02-20 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0014_alter_waterbillpayment_billing_month_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waterbillpayment',
            name='consumer_number',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
