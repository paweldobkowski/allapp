# Generated by Django 4.0.2 on 2022-04-28 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_fightermodel_coins'),
    ]

    operations = [
        migrations.AddField(
            model_name='fightermodel',
            name='average',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
