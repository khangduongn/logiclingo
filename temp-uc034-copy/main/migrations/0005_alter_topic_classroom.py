from django.db import migrations, models
import django.db.models.deletion

def set_default_classroom(apps, schema_editor):
    Topic = apps.get_model('main', 'Topic')
    Classroom = apps.get_model('main', 'Classroom')
    
    # Get the first classroom or create one if none exists
    default_classroom, created = Classroom.objects.get_or_create(
        className='Default Classroom',
        defaults={
            'startDate': '2025-01-01',
            'endDate': '2025-12-31',
            'instructorName': 'System'
        }
    )
    
    # Update all topics without a classroom
    Topic.objects.filter(classroom__isnull=True).update(classroom=default_classroom)

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_topic_classroom_topic_completed'),
    ]

    operations = [
        migrations.RunPython(set_default_classroom),
        migrations.AlterField(
            model_name='topic',
            name='classroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='main.classroom'),
        ),
    ] 