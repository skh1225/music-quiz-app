# Generated by Django 3.2.20 on 2023-08-09 07:39

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_room_music_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='music',
            name='image_file',
            field=models.ImageField(null=True, upload_to=core.models.music_image_file_path),
        ),
    ]
