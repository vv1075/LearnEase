# Generated by Django 4.2.20 on 2025-03-13 13:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learneaseapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quiz_id', models.CharField(max_length=100)),
                ('assigned_students', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
