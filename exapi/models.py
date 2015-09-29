from django.db import models
from enumfields import Enum, EnumField
from django.utils import timezone
from datetime import datetime
import pytz
import exapi

# Create your models here.

class Gallery(models.Model):
    gid = models.IntegerField(primary_key=True)
    token = models.CharField(max_length=12)

    def get_meta(self):
        print self.pk
        if not hasattr(self, 'gallerymeta'):
            meta = GalleryMeta()
            try:
                api_resp = exapi.get_meta(self.gid, self.token)
            except ValueError:
                raise
            except RuntimeError as e:
                print 'Unexpected error:', e
                raise
            meta.title = api_resp['title']
            meta.title_jpn = api_resp.get('title_jpn', u'')
            meta.category = Category(api_resp['category'])
            meta.thumb_url = api_resp['thumb']
            meta.uploader = api_resp['uploader']
            meta.images = int(api_resp['filecount'])
            meta.image_size = api_resp['filesize']
            meta.deleted = api_resp['expunged']
            meta.rating = float(api_resp['rating'])
            meta.gallery = self
            meta.gallery_id = self.pk
            meta.created_at = timezone.localtime(datetime.fromtimestamp(int(api_resp['posted']), tz=pytz.utc))
            meta.save()
            # meta.pk = self.pk
            tags = []
            for tag in api_resp['tags']:
                if ':' in tag:
                    namespace, name = tag.split(':', 1)
                else:
                    namespace, name = '', tag

                tag, _ = GalleryTag.objects.get_or_create(name=name, namespace=TagNamespace(namespace))
                tags.append(tag)
            print self.gallerymeta.pk
            self.gallerymeta.tags.add(*tags)
        return self.gallerymeta


class TagNamespace(Enum):
        ARTIST = 'artist'
        CHARACTER = 'character'
        FEMALE = 'female'
        GROUP = 'group'
        LANGUAGE = 'language'
        MALE = 'male'
        PARODY = 'parody'
        RECLASS = 'reclass'
        DEFAULT = ''

class GalleryTag(models.Model):
    class Meta:
        verbose_name = 'Gallery Tag'
        verbose_name_plural = 'Gallery Tags'
        unique_together = (
            ('namespace', 'name'),
        )

    namespace = EnumField(TagNamespace, blank=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name if not self.namespace.value else self.namespace.value + ':' + self.name

    def __unicode__(self):
        return self.name if not self.namespace.value else self.namespace.value + ':' + self.name

class Category(Enum):
    DOUJINSHI = 'Doujinshi'
    MANGA = 'Manga'
    ARTIST_CG = 'Artist CG Sets'
    GAME_CG = 'Game CG Sets'
    WESTERN = 'Western'
    IMAGE_SET = 'Image Sets'
    NON_H = 'Non-H'
    COSPLAY = 'Cosplay'
    ASIAN_PORN = 'Asian Porn'
    MISC = 'Misc'
    PRIVATE = 'Private'


class GalleryMeta(models.Model):
    gallery = models.OneToOneField(Gallery, primary_key=True)
    title = models.CharField(max_length=255, db_index=True)
    title_jpn = models.CharField(max_length=255, db_index=True, blank=True)
    category = EnumField(Category, db_index=True, max_length=20)
    thumb_url = models.TextField()
    uploader = models.CharField(max_length=80, db_index=True)
    images = models.IntegerField()
    image_size = models.IntegerField()
    deleted = models.BooleanField(default=False)
    rating = models.FloatField()
    tags = models.ManyToManyField(GalleryTag)

    created_at = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update(self):
        #TODO: Implement update method, with minimal lifetime check.
        pass
