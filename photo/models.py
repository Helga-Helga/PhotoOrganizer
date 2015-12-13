import os
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.files import File
from string import join
from os.path import join as pjoin
from PIL import Image as PImage
from PhotoOrganizer.settings import MEDIA_ROOT
from tempfile import *


class Album(models.Model):
    title = models.CharField(max_length=60)
    public = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    def images(self):
        lst = [x.image.name for x in Image.objects.all()]
        lst = ["<a href='/media/%s'>%s</a>" % (x, x.split('/')[-1]) for x in lst]
        return join(lst, ', ')
    images.allow_tags = True


class Tag(models.Model):
    tag = models.CharField(max_length=50)

    def __unicode__(self):
        return self.tag


class Image(models.Model):
    title = models.CharField(max_length=60, blank=True, null=True)
    image = models.FileField(upload_to="images/")
    tags = models.ManyToManyField(Tag, blank=True)
    albums = models.ManyToManyField(Album, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=50)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True)
    thumbnail2 = models.ImageField(upload_to="images/", blank=True, null=True)
    thumb = models.ImageField(upload_to="images/", blank=True, null=True)

    def save(self, *args, **kwargs):
        """Save image dimensions."""
        super(Image, self).save(*args, **kwargs)
        im = PImage.open(pjoin(MEDIA_ROOT, self.image.name))
        self.width, self.height = im.size

        # Large thumbnail
        fn, ext = os.path.splitext(self.image.name)
        im.thumbnail((256, 256), PImage.ANTIALIAS)
        thumb_fn = fn + "-thumb2" + ext
        tf2 = NamedTemporaryFile()
        im.save(tf2.name, "JPEG")
        self.thumbnail2.save(thumb_fn, File(open(tf2.name)), save=False)
        tf2.close()

        super(Image, self).save(*args, **kwargs)

    def size(self):
        """Image size."""
        return "%s x %s" % (self.width, self.height)

    def __unicode__(self):
        return self.image.name

    def tags_(self):
        lst = [tag.tag for tag in Tag.objects.filter(image=self)]
        return str(join(lst, ', '))

    def albums_(self):
        lst = [album.title for album in Album.objects.filter(image=self)]
        return str(join(lst, ', '))

    def thumbnail(self):
        return """<a href="%s"><img border="0" alt="" src="%s" height="40" /></a>""" % (
            (self.image.url, self.image.url))

    thumbnail.allow_tags = True


class AlbumAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "images"]


class TagAdmin(admin.ModelAdmin):
    list_display = ["tag"]


class ImageAdmin(admin.ModelAdmin):
    # search_fields = ["title"]
    list_display = ["title", "user", "rating", "size", "tags_", "albums_", "thumbnail", "created"]
    list_filter = ["tags", "albums", "user"]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(Album, AlbumAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Image, ImageAdmin)

