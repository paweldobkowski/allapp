# Generated by Django 4.0.2 on 2022-04-29 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_fightermodel_average'),
    ]

    operations = [
        migrations.AddField(
            model_name='fightermodel',
            name='injury',
            field=models.TextField(default='none'),
        ),
    ]