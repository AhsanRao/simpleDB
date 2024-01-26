# Generated by Django 4.1.12 on 2024-01-26 07:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0021_equipment_business"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="business",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="home.business",
            ),
        ),
    ]