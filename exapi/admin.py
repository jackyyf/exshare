from django.contrib import admin
from .models import Gallery, GalleryMeta, GalleryTag

# Register your models here.

class MetaInline(admin.StackedInline):
    model = GalleryMeta

class GalleryFull(admin.ModelAdmin):
    inlines = (MetaInline, )

admin.site.register([GalleryMeta, GalleryTag])
admin.site.register(Gallery, GalleryFull)