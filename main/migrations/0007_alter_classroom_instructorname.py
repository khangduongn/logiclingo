# Generated by Django 5.1.5 on 2025-02-27 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_remove_classroom_instructorlastname_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="classroom",
            name="instructorName",
            field=models.CharField(default="", max_length=200),
        ),
    ]
