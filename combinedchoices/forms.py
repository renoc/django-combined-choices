from django.apps import apps
from django.conf import settings
from django.forms.fields import BooleanField, CharField
from django.forms.forms import Form
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple, RadioSelect, Textarea

from combinedchoices.models import (
    THROUGH_MODEL, SECTION_MODEL, Choice, CompletedCCO)


class ChoiceLabelMixin(object):

    def label_from_instance(self, obj):
        return obj.text


class MultiChoice (ChoiceLabelMixin, ModelMultipleChoiceField):
    pass


class SingleChoice (ChoiceLabelMixin, ModelChoiceField):
    pass


class ReadyForm(Form):
    form_name = CharField(label='Completed Name')

    def __init__(self, *args, **kwargs):
        ready_obj = kwargs.pop('ready_obj')
        filters = kwargs.pop('filters', {})
        super(ReadyForm, self).__init__(*args, **kwargs)
        baseccobjs = ready_obj.included_forms.filter(**filters)
        for section in self.get_sections(baseccobjs, **filters):
            if section.cross_combine:
                name = section.field_name
                queryset = Choice.objects.filter(
                    choice_section__base_ccobj__in=baseccobjs)
                self.create_section_field(name, section, queryset)
            else:
                for basecc in baseccobjs:
                    name = '%s - %s' % (
                        basecc.form_name, section.field_name)
                    queryset = Choice.objects.filter(
                        choice_section__base_ccobj=basecc)
                    self.create_section_field(name, section, queryset)

    def create_section_field(self, name, basechoice, queryset):
        Section = apps.get_model(*SECTION_MODEL.split('.'))
        queryset = queryset.filter(
            choice_section__base_choice=basechoice).order_by('text')
        if basechoice.field_type in [Section.TEXT, Section.DESCRIPTION]:
            self.fields[name] = CharField(
                help_text=basechoice.instructions, required=False,
                initial='\n\n'.join(queryset.values_list('text', flat=True)))
            self.fields[name].widget = Textarea()
            if basechoice.field_type is Section.DESCRIPTION:
                self.fields[name].widget.attrs.update(
                    {'class':'combo-text', 'disabled':True})
            elif basechoice.field_type is Section.TEXT:
                self.fields[name].widget.attrs.update(
                    {'class':'combo-text', 'read-only':True})
        elif basechoice.field_type is Section.SINGLE:
            self.fields[name] = SingleChoice(
                queryset=queryset, help_text=basechoice.instructions,
                empty_label='')
            self.fields[name].widget = RadioSelect(
                choices=self.fields[name].choices)
        else:
            self.fields[name] = MultiChoice(
                queryset=queryset, help_text=basechoice.instructions)
            self.fields[name].widget = CheckboxSelectMultiple(
                choices=self.fields[name].choices)
        self.fields[name].label = name

    def get_sections(self, compendiums, **kwargs):
        kwargs.update({THROUGH_MODEL.split('.')[1].lower() +
                      '__base_ccobj__in':compendiums})
        model = apps.get_model(*SECTION_MODEL.split('.'))
        return model.objects.filter(**kwargs)

    def save(self, *args, **kwargs):
        completed = {}
        name = self.cleaned_data.pop('form_name')
        self.fields.pop('form_name')
        for field in self.fields.keys():
            data = self.cleaned_data[field]
            if not data:
                pass
            elif type(self.fields[field]) is CharField:
                completed[field] = [data]
            elif type(self.fields[field]) is SingleChoice:
                completed[field] = [data.text]
            elif type(self.fields[field]) in [MultiChoice]:
                completed[field] = []
                for choice in self.cleaned_data[field]:
                    completed[field].append(choice.text)
            else:
                raise NotImplementedError()
        return CompletedCCO.objects.create(
            form_name=name, form_data=completed, **kwargs)
