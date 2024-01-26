# Generated by Django 4.1.12 on 2024-01-26 15:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0022_person_business"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="role",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Administrator"),
                    ("CLIENT", "Client"),
                    ("EXEC", "Executive"),
                    ("LEGAL", "Legal"),
                    ("ACCT", "Accountant"),
                ],
                max_length=255,
            ),
        ),
    ]