from django.forms.fields import BooleanField, CharField
from django.forms.forms import Form

import models


class ReadyForm(Form):
    form_name = CharField(label='Completed Name')

    def get_sections(self, compendiums, **kwargs):
        kwargs.update({models.THROUGH_MODEL.split('.')[1].lower() +
                      '__base_ccobj__in':compendiums})
        model = models.models.get_model(*models.SECTION_MODEL.split('.'))
        return model.objects.filter(**kwargs)
