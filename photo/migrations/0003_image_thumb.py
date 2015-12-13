# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0002_image_thumbnail2'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='thumb',
            field=models.ImageField(null=True, upload_to=b'images/', blank=True),
        ),
    ]
