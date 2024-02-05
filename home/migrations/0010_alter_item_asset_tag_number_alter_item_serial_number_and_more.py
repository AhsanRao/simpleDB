# Generated by Django 4.1.12 on 2024-02-04 20:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0009_alter_person_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="asset_tag_number",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="item",
            name="serial_number",
            field=models.CharField(max_length=255),
        ),
        migrations.AddConstraint(
            model_name="item",
            constraint=models.UniqueConstraint(
                fields=("asset_tag_number", "business"),
                name="unique_asset_tag_per_business",
            ),
        ),
        migrations.AddConstraint(
            model_name="item",
            constraint=models.UniqueConstraint(
                fields=("serial_number", "business"),
                name="unique_serial_number_per_business",
            ),
        ),
    ]
