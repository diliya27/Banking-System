# Generated by Django 5.1.5 on 2025-02-13 10:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposittransaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposit_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Kseb_Billpay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consumer_number', models.IntegerField()),
                ('bill_number', models.IntegerField(unique=True)),
                ('bill_amt', models.IntegerField()),
                ('due_date', models.DateField()),
                ('payment_date', models.DateField(auto_now=True)),
                ('transaction_id', models.CharField(max_length=50, unique=True)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')], max_length=15)),
                ('mode_of_payment', models.CharField(choices=[('UPI', 'UPI'), ('Net Banking', 'Net Banking'), ('Debit Card', 'Debit Card'), ('Credit Card', 'Credit Card')], max_length=20)),
                ('account_number', models.BigIntegerField()),
                ('bank_name', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
