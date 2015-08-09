from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from jsonfield import JSONField


class BaseChoice(models.Model):
    DESCRIPTION = 0  # outputed with no input
    SINGLE = 1  # radio button
    MULTIPLE = 2  # checkboxes
    NUMBER = 3  # number input
    TEXT = 4  # text input
    CHOICE_TYPES = (
        (DESCRIPTION, 'Description'),
        (SINGLE, 'Single'),
        (MULTIPLE, 'Multiple'),
        (NUMBER, 'Number'),
        (TEXT, 'Text'),
    )
    cross_combine = models.BooleanField(default=True)
    field_name = models.CharField(max_length=64, null=False, blank=False)
    field_type = models.IntegerField(
        choices=CHOICE_TYPES, null=False, blank=False)
    instructions = models.TextField(null=False, blank=True, default='')
    min_selects = models.IntegerField(null=False, default=1)
    max_selects = models.IntegerField(null=False, default=1)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.field_name

    @property
    def choice_type(self):
        return self.CHOICE_TYPES[self.field_type][1]

    def validate_unique(self, exclude=None):
        super(BaseChoice, self).validate_unique(exclude=exclude)
        duplicates = type(self).objects.exclude(id=self.id).filter(
            field_name=self.field_name)
        if duplicates.exists():
            raise ValidationError(('Non-Unique Name Error'), code='invalid')

#    def values(self, queryset):
#        assert(queryset.objects.class == BaseCCObj)
#        return Choice.objects.filter(
#            choice_field.base_choice=self,
#            choice_field.base_ccobj__in=queryset)


SECTION_MODEL = getattr(
    settings, 'SECTION_MODEL', 'combinedchoices.fake_models.BaseChoice')
THROUGH_MODEL = getattr(
    settings, 'THROUGH_MODEL', 'combinedchoices.fake_models.ChoiceSection')


class BaseCCObj(models.Model):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    choice_sections = models.ManyToManyField(
        SECTION_MODEL, through=THROUGH_MODEL, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.form_name

    def base_choices(self):
        return self.choice_sections.all()


BASE_MODEL = getattr(
    settings, 'BASE_MODEL', 'combinedchoices.fake_models.BaseCCObj')


class ChoiceSection(models.Model):
    base_ccobj = models.ForeignKey(BASE_MODEL, null=False, blank=False)
    base_choice = models.ForeignKey(SECTION_MODEL, null=False, blank=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s - %s' % (self.base_ccobj, self.base_choice)


class Choice(models.Model):
    choice_section = models.ForeignKey(THROUGH_MODEL, null=False, blank=False)
    text = models.TextField(null=False, blank=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.text[:20]


class ReadyCombinedObj(models.Model):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    included_forms = models.ManyToManyField(BASE_MODEL, null=False, blank=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.form_name


class CompletedCombinedObj(models.Model):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    form_data = JSONField(default={})

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.form_name
