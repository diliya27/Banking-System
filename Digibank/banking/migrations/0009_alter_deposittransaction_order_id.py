# Generated by Django 5.1.5 on 2025-02-18 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0008_alter_deposittransaction_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposittransaction',
            name='order_id',
            field=models.CharField(max_length=500, null=True, unique=True),
        ),
    ]
