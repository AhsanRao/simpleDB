# Generated by Django 4.1.12 on 2024-01-25 12:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0012_user_business_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="business",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
