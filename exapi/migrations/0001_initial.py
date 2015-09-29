# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import enumfields.fields
import exapi.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('gid', models.IntegerField(serialize=False, primary_key=True)),
                ('token', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='GalleryTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('namespace', enumfields.fields.EnumField(blank=True, max_length=10, enum=exapi.models.TagNamespace)),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
                'verbose_name': 'Gallery Tag',
                'verbose_name_plural': 'Gallery Tags',
            },
        ),
        migrations.CreateModel(
            name='GalleryMeta',
            fields=[
                ('gallery', models.OneToOneField(primary_key=True, serialize=False, to='exapi.Gallery')),
                ('title', models.CharField(max_length=255, db_index=True)),
                ('title_jpn', models.CharField(db_index=True, max_length=255, blank=True)),
                ('category', enumfields.fields.EnumField(db_index=True, max_length=20, enum=exapi.models.Category)),
                ('thumb_url', models.TextField()),
                ('uploader', models.CharField(max_length=80, db_index=True)),
                ('images', models.IntegerField()),
                ('image_size', models.IntegerField()),
                ('deleted', models.BooleanField(default=False)),
                ('rating', models.FloatField()),
                ('created_at', models.DateTimeField()),
                ('fetched_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='gallerytag',
            unique_together=set([('namespace', 'name')]),
        ),
        migrations.AddField(
            model_name='gallerymeta',
            name='tags',
            field=models.ManyToManyField(to='exapi.GalleryTag'),
        ),
    ]
