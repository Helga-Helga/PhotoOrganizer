from collections import defaultdict

from django.conf.global_settings import MEDIA_URL
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf

from photo.models import Album, Image, ImageForm, AlbumForm


def main(request):
    """Main listing."""
    albums = Album.objects.all()
    if not request.user.is_authenticated():
        albums = albums.filter(public=True)

    for album in albums:
        album.images = album.image_set.all().extra(select={'size': '(1.*width)/height'}, order_by=['-size'])

    return render_to_response("photo/list.html", dict(albums=albums, user=request.user))


def album(request, pk, view="thumbnail"):
    """Album listing."""

    album = Album.objects.get(pk=pk)
    if not album.public and not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in to view this album.")
    images = album.image_set.all().extra(select={'size': '(1.*width)/height'}, order_by=['-size'])

    for img in images:
        img.album_lst = [x[1] for x in img.albums.values_list()]
    if 'HTTP_REFERER' in request.META:
        backurl = request.META["HTTP_REFERER"]
    else:
        backurl = '/'
    d = dict(album=album, images=images, user=request.user, view=view, albums=Album.objects.all(), media_url=MEDIA_URL,
             backurl=backurl)
    d.update(csrf(request))
    return render_to_response("photo/album.html", d)


def image(request, pk):
    """Image page."""
    img = Image.objects.get(pk=pk)
    if 'HTTP_REFERER' in request.META:
        backurl = request.META["HTTP_REFERER"]
    else:
        backurl = '/'
    return render_to_response("photo/image.html", dict(image=img, user=request.user,
                                                       backurl=backurl, media_url=MEDIA_URL))


def update(request):
    """Updating image, title, rating, albums."""
    p = request.POST
    images = defaultdict(dict)

    # Create dictionary of properties for each image
    for k, v in p.items():
        if k.startswith("title") or k.startswith("rating"):
            k, pk = k.split('-')
            images[pk][k] = v
        elif k.startswith("album"):
            pk = k.split('-')[1]
            images[pk]["albums"] = p.getlist(k)


    # Process properties, assign to image objects and save
    for k, d, in images.items():
        image = Image.objects.get(pk=k)
        image.title = d["title"]
        image.rating = int(d["rating"])

    if "albums" in d:
        image.albums = d["albums"]
        image.save()

    return HttpResponseRedirect(request.META["HTTP_REFERER"], dict(media_url=MEDIA_URL))


def add(request):
    """Updating image, title, rating, albums."""
    d = dict()
    d.update(csrf(request))
    d['media_url'] = MEDIA_URL
    d['user'] = request.user
    if not request.POST:
        d['image_form'] = ImageForm()
        return render_to_response("photo/add.html", d)

    image_form = ImageForm(request.POST, request.FILES)
    if image_form.is_valid():
        image_form.save()
        return redirect('photo.views.main')
    else:
        d['image_form'] = image_form
    return render_to_response("photo/add.html", d)


def add_album(request):
    d = dict()
    d.update(csrf(request))
    d['media_url'] = MEDIA_URL
    d['user'] = request.user
    if not request.POST:
        d['album_form'] = AlbumForm()
        return render_to_response("photo/add_album.html", d)

    album_form = AlbumForm(request.POST)
    if album_form.is_valid():
        album_form.save()
        return redirect('photo.views.main')
    else:
        d['image_form'] = album_form
    return render_to_response("photo/add_album.html", d)
