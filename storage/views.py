import os
import random

from annoying.decorators import render_to, ajax_request
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponse
from django.utils.translation import ugettext as _
import PIL

from .forms import ImageForm
from .models import Image


@render_to('index.html')
def index(request):
    result = {'images': Image.objects.filter(deleted=False).order_by('-pk')}
    if result['images'].count():
        result['random_image'] = Image.objects.filter(deleted=False).order_by('?')[0]
        result['random_image_resize_url'] = reverse(
            'resize',
            args=(result['random_image'].pk, random.randint(100, 500), random.randint(100, 500)))
    return result


@ajax_request
def upload(request):
    if request.method == 'POST':
        image = Image()
        image.save()
        form = ImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return {'success': True, 'url': image.file.url}
        else:
            image.delete()
            return {'success': False, 'message': form.errors.get('file')}
    return {'success': False, 'message': _('POST method required')}


def resize(request, image_pk, width_str, height_str):
    db_image = Image.objects.get(pk=image_pk)
    response = HttpResponse(mimetype=db_image.content_type or 'image')
    width, height = int(width_str), int(height_str)

    if settings.ALLOW_CACHE_RESIZED_IMAGES:
        resized_path = list(os.path.splitext(db_image.file.path))
        resized_path.insert(1, '_%dx%d' % (width, height))
        resized_path = ''.join(resized_path)
        if os.path.exists(resized_path):
            response.content = file(resized_path)
            return response

    image_type = db_image.content_type.replace('image/', '').upper()
    image = PIL.Image.open(db_image.file).convert('RGBA')
    resized = image.resize((int(width), int(height)), PIL.Image.ANTIALIAS)

    if settings.ALLOW_CACHE_RESIZED_IMAGES:
        resized.save(resized_path, image_type)
    resized.save(response, image_type)
    return response
