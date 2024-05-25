# Generated by Django 5.0.4 on 2024-05-25 08:20

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0009_alter_song_albums_alter_song_playlists'),
    ]

    operations = [
        migrations.RenameField(
            model_name='song',
            old_name='like_count',
            new_name='view_count',
        ),
        migrations.AddField(
            model_name='song',
            name='upload_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
