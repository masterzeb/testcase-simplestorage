from django.conf import settings
from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext as _

from .models import Image


ALLOWED_CONTENT_TYPES = (u'image/png', u'image/jpeg', u'image/gif')


class ImageForm(ModelForm):
    class Meta:
        model = Image

    def clean_file(self):
        data = self.cleaned_data.get('file')
        if data.size > settings.IMAGE_MAX_SIZE_KB:
            raise ValidationError(_('File too large'))
        if not data.content_type in ALLOWED_CONTENT_TYPES:
            raise ValidationError(_('Wrong content type'))

        self.file_content_type = data.content_type
        return data

    def clean(self):
        self.cleaned_data['content_type'] = self.file_content_type
        return self.cleaned_data
