from django.apps import apps
from django.forms.fields import BooleanField, CharField, MultiValueField
from django.forms.forms import Form
from django.forms.models import (
    ModelForm, ModelChoiceField, ModelMultipleChoiceField)
from django.forms.widgets import (
    CheckboxSelectMultiple, MultiWidget, NumberInput, RadioSelect, Textarea)
from extra_views import InlineFormSet
import json

from combinedchoices.models import (
    BaseCCO, Choice, ChoiceSection, CompletedCCO, ReadyCCO, Section)


class ChoiceLabelMixin(object):
    def label_from_instance(self, obj):
        return obj.text


class MultiChoice(ChoiceLabelMixin, ModelMultipleChoiceField):
    pass


class mNumberWidget(NumberInput):

    def render(self, *args, **kwargs):
        input_box = super(mNumberWidget, self).render(*args, **kwargs)
        return '<p><label>%s</label>%s</p>' % (self.attrs['label'], input_box)


class mNumberField(CharField):
    widget = mNumberWidget

    def widget_attrs(self, widget):
        attrs = super(mNumberField, self).widget_attrs(widget)
        attrs['label'] = self.label
        return attrs


class MultiNumberField(ChoiceLabelMixin, MultiValueField):

    def __init__(self, fields=(), *args, **kwargs):
        widgets = [field.widget for field in fields]
        self.widget = MultiWidget(widgets=widgets)
        initial = [field.initial for field in fields]
        return super(MultiNumberField, self).__init__(
            fields=fields, *args, initial=initial, **kwargs)

    def compress(self, values):
        return json.dumps(values)


class SingleChoice(ChoiceLabelMixin, ModelChoiceField):
    pass


class BaseCCOForm(ModelForm):
    class Meta:
        model = BaseCCO
        fields = ('form_name',)


class SectionForm(ModelForm):
    class Meta:
        model = Section
        exclude = ['user']


class ChoiceSectionForm(ModelForm):
    class Meta:
        model = Choice
        exclude = []


class ChoiceForm(InlineFormSet):
    model = Choice


class CombineForm(ModelForm):
    class Meta:
        model = ReadyCCO
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        cco_queryset = kwargs.pop('cco_queryset')
        super(CombineForm, self).__init__(*args, **kwargs)
        self.fields['included_forms'].widget = CheckboxSelectMultiple(
            choices=self.fields['included_forms'].choices)
        self.fields['included_forms'].queryset = cco_queryset


class ReadyForm(Form):
    form_name = CharField(label='Completed Name')

    def __init__(self, *args, **kwargs):
        ready_obj = kwargs.pop('ready_obj')
        filters = self.filters = self.get_filters(ready_obj)
        super(ReadyForm, self).__init__(*args, **kwargs)
        baseccobjs = ready_obj.included_forms.filter(**filters)
        for section in self.get_sections(baseccobjs, **filters):
            if section.cross_combine:
                name = section.field_name
                queryset = Choice.objects.filter(
                    choice_section__basecco__in=baseccobjs).order_by('text')
                self.create_section_field(name, section, queryset)
            else:
                for basecc in baseccobjs.filter(sections=section):
                    name = '%s - %s' % (
                        basecc.form_name, section.field_name)
                    queryset = Choice.objects.filter(
                        choice_section__basecco=basecc)
                    self.create_section_field(name, section, queryset)

    def create_section_field(self, name, basechoice, queryset):
        queryset = queryset.filter(
            choice_section__section=basechoice)
        if basechoice.field_type in [Section.TEXT, Section.DESCRIPTION]:
            self.fields[name] = CharField(
                help_text=basechoice.instructions, required=False,
                initial='\n\n'.join(queryset.values_list('text', flat=True)))
            self.fields[name].widget = Textarea()
            self.fields[name].widget.attrs.update({'class':'combo-text'})
            if basechoice.field_type is Section.DESCRIPTION:
                self.fields[name].widget.attrs.update(
                    {'class':'combo-readonly', 'read-only':True})
        elif basechoice.field_type is Section.SINGLE:
            self.fields[name] = SingleChoice(
                queryset=queryset, help_text=basechoice.instructions,
                empty_label='')
            self.fields[name].widget = RadioSelect(
                choices=self.fields[name].choices)
        elif basechoice.field_type is Section.NUMBER:
            self.fields[name] = MultiNumberField(
                fields=[
                    mNumberField(
                        initial='%s' % basechoice.min_selects, label=label,
                        required=True)
                    for label in queryset.values_list('text', flat=True)],
                help_text=basechoice.instructions)
            return
        else:
            self.fields[name] = MultiChoice(
                queryset=queryset, help_text=basechoice.instructions)
            self.fields[name].widget = CheckboxSelectMultiple(
                choices=self.fields[name].choices)
        self.fields[name].label = name

    def get_filters(self, ready_obj):
        return {'user':ready_obj.user}

    def get_sections(self, compendiums, **kwargs):
        kwargs.update({'choicesection__basecco__in':compendiums})
        return Section.objects.filter(**kwargs)

    def save(self, *args, **kwargs):
        completed = {}
        name = self.cleaned_data.pop('form_name')
        self.fields.pop('form_name')
        for field in self.fields.keys():
            data = self.cleaned_data[field]
            if not data:
                pass
            elif type(self.fields[field]) is CharField:
                completed[field] = data
            elif type(self.fields[field]) is SingleChoice:
                completed[field] = data.text
            elif type(self.fields[field]) in [MultiChoice]:
                completed[field] = []
                for choice in self.cleaned_data[field]:
                    completed[field].append(choice.text)
            elif type(self.fields[field]) is MultiNumberField:
                data = json.loads(data)
                completed[field] = {}
                for subfield in range(len(data)):
                    completed[field][
                        self.fields[field].fields[subfield].label
                        ] = data[subfield]
            else:
                raise NotImplementedError()
        kwargs.update(self.filters)
        return CompletedCCO.objects.create(
            form_name=name, form_data=completed, **kwargs)
