# Generated by Django 4.1.12 on 2024-01-31 14:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0004_sale_billing_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sale",
            name="renewal_date",
        ),
    ]
