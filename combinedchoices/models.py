from django.core.exceptions import ValidationError
from django.db import models
from jsonfield import JSONField


class BaseChoice(models.Model):
    DESCRIPTION = 0  # text not displayed on final ouput
    SINGLE = 1
    MULTIPLE = 2
    NUMBER = 3
    TEXT = 4
    CHOICE_TYPES = (
        (DESCRIPTION, 'Description'),
        (SINGLE, 'Single'),
        (MULTIPLE, 'Multiple'),
        (NUMBER, 'Number'),
        (TEXT, 'Text'),
    )
    cross_combine = models.BooleanField(default=False)
    field_name = models.CharField(max_length=64, null=False, blank=False)
    field_type = models.IntegerField(
        choices=CHOICE_TYPES, null=False, blank=False)
    instructions = models.TextField(null=False, blank=True, default='')
    min_selects = models.IntegerField(null=False, default=1)
    max_selects = models.IntegerField(null=False, default=1)

    def validate_unique(self, exclude=None):
        super(BaseChoice, self).validate_unique(exclude=exclude)
        duplicates = BaseChoice.objects.exclude(id=self.id).filter(
            field_name=self.field_name)
        if duplicates.exists():
            raise ValidationError(('Non-Unique Name Error'), code='invalid')

    def __unicode__(self):
        return self.field_name

    @property
    def choice_type(self):
        return self.CHOICE_TYPES[self.field_type][1]

#    def values(self, queryset):
#        assert(queryset.objects.class == BaseCCObj)
#        return Choice.objects.filter(
#            choice_field.base_choice=self,
#            choice_field.base_ccobj__in=queryset)


class BaseCCObj(models.Model):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    choice_fields = models.ManyToManyField(
        BaseChoice, through='ChoiceField', blank=True)

    def __unicode__(self):
        return self.form_name

    def base_choices(self):
        return self.choice_fields.all()


class ChoiceField(models.Model):
    base_ccobj = models.ForeignKey(BaseCCObj, null=False, blank=False)
    base_choice = models.ForeignKey(BaseChoice, null=False, blank=False)

    def __unicode__(self):
        return '%s - %s' % (self.base_ccobj, self.base_choice)


class Choice(models.Model):
    choice_field = models.ForeignKey(ChoiceField, null=False, blank=False)
    text = models.TextField(null=False, blank=False)


class CompletedCombinedObj(models.Model):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    form_data = JSONField(default='{}')

    def __unicode__(self):
        return self.form_name


class ReadyCombinedObj(models.Model):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    included_forms = models.ManyToManyField(
        BaseCCObj, null=False, blank=False)


    def __unicode__(self):
        return self.form_name
