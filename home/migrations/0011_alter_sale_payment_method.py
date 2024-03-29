# Generated by Django 4.1.12 on 2024-02-04 21:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0010_alter_item_asset_tag_number_alter_item_serial_number_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="payment_method",
            field=models.CharField(
                choices=[("One-time", "One-Time"), ("Recurring", "Recurring")],
                default="One-time",
                max_length=20,
            ),
        ),
    ]
