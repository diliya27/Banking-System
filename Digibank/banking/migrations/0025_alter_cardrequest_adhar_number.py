# Generated by Django 5.1.2 on 2025-03-27 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0024_billhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardrequest',
            name='adhar_number',
            field=models.CharField(max_length=20),
        ),
    ]
