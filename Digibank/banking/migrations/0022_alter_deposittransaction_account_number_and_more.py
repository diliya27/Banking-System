# Generated by Django 5.1.5 on 2025-03-26 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0021_alter_deposittransaction_account_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposittransaction',
            name='account_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='deposittransaction',
            name='ifsc_code',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]
