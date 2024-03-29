# Generated by Django 4.1.12 on 2024-02-04 19:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0005_remove_sale_renewal_date"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Product",
        ),
        migrations.AddConstraint(
            model_name="person",
            constraint=models.UniqueConstraint(
                fields=("email", "business"), name="unique_email_per_business"
            ),
        ),
    ]
