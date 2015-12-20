from collections import defaultdict

from django.conf.global_settings import MEDIA_URL
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from photo.models import Album, Image


def main(request):
    """Main listing."""
    albums = Album.objects.all()
    if not request.user.is_authenticated():
        albums = albums.filter(public=True)

    paginator = Paginator(albums, 10)
    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        albums = paginator.page(page)
    except (InvalidPage, EmptyPage):
        albums = paginator.page(paginator.num_pages)

    for album in albums.object_list:
        album.images = album.image_set.all()

    return render_to_response("photo/list.html", dict(albums=albums, user=request.user))


def album(request, pk, view="thumbnail"):
    """Album listing."""
    num_images = 30
    if view == "full":
        num_images = 10

    album = Album.objects.get(pk=pk)
    if not album.public and not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in to view this album.")
    images = album.image_set.all()
    paginator = Paginator(images, num_images)
    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        images = paginator.page(page)
    except (InvalidPage, EmptyPage):
        images = paginator.page(paginator.num_pages)

    for img in images.object_list:
        img.album_lst = [x[1] for x in img.albums.values_list()]

    d = dict(album=album, images=images, user=request.user, view=view, albums=Album.objects.all(), media_url=MEDIA_URL,
             backurl=request.META["HTTP_REFERER"])
    d.update(csrf(request))
    return render_to_response("photo/album.html", d)


def image(request, pk):
    """Image page."""
    img = Image.objects.get(pk=pk)
    return render_to_response("photo/image.html", dict(image=img, user=request.user,
                                                       backurl=request.META["HTTP_REFERER"], media_url=MEDIA_URL))


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
