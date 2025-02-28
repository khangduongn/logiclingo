# Generated by Django 5.1.5 on 2025-02-27 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_alter_student_classrooms"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="classroom",
            name="instructorLastName",
        ),
        migrations.RemoveField(
            model_name="instructor",
            name="classrooms",
        ),
        migrations.RemoveField(
            model_name="student",
            name="classrooms",
        ),
        migrations.AddField(
            model_name="classroom",
            name="instructorName",
            field=models.CharField(default="Unknown", max_length=200),
        ),
        migrations.AddField(
            model_name="classroom",
            name="instructors",
            field=models.ManyToManyField(
                related_name="classrooms", to="main.instructor"
            ),
        ),
        migrations.AddField(
            model_name="classroom",
            name="students",
            field=models.ManyToManyField(
                blank=True, related_name="classrooms", to="main.student"
            ),
        ),
    ]
