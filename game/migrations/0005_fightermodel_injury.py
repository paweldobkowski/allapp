# Generated by Django 4.0.2 on 2022-05-05 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_remove_fightermodel_injury'),
    ]

    operations = [
        migrations.AddField(
            model_name='fightermodel',
            name='injury',
            field=models.FloatField(default=0.0),
        ),
    ]
