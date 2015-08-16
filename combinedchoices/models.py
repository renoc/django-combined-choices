from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import get_object_or_404
from jsonfield import JSONField


class UserModelManager(models.QuerySet):

    def get_user_objects(self, user):
        return self.filter(user=user)

    def get_or_404(self, *args, **kwargs):
        return get_object_or_404(self.model, *args, **kwargs)


class UserModelMixin(models.Model):
    SELF_FILTER = ['user']
    user = models.ForeignKey(User, null=True, blank=True)
    objects = UserModelManager.as_manager()

    class Meta:
        abstract = True

    def self_kwargs(self):
        kwargs = {}
        for selfilter in self.SELF_FILTER:
            kwargs.update({selfilter: getattr(self, selfilter, None)})
        return kwargs

    def unicode_prefex(self):
        if self.user:
            return '%s - ' % self.user
        else:
            return ''


ModelMixin = UserModelMixin


class Section(ModelMixin):
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

    def __unicode__(self):
        return '%s%s' % (self.unicode_prefex(), self.field_name)

    @property
    def choice_type(self):
        return self.CHOICE_TYPES[self.field_type][1]

    def validate_unique(self, exclude=None):
        super(Section, self).validate_unique(exclude=exclude)
        duplicates = type(self).objects.exclude(id=self.id).filter(
            field_name=self.field_name, **self.self_kwargs())
        if duplicates.exists():
            raise ValidationError(('Non-Unique Name Error'), code='invalid')


class BaseCCO(ModelMixin):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    choice_sections = models.ManyToManyField(
        Section, through='ChoiceSection', blank=True)

    def __unicode__(self):
        return '%s%s' % (self.unicode_prefex(), self.form_name)

    @property
    def name(self):
        return self.form_name

    def available_sections(self):
        return Section.objects.filter(**self.self_kwargs()).exclude(
            basecco=self)

    def base_choices(self):
        return self.choice_sections.all()


class ChoiceSection(models.Model):
    base_ccobj = models.ForeignKey(BaseCCO, null=False, blank=False)
    base_choice = models.ForeignKey(Section, null=False, blank=False)

    def __unicode__(self):
        return '%s - %s' % (self.base_ccobj, self.base_choice)


class Choice(models.Model):
    choice_section = models.ForeignKey(ChoiceSection, null=False, blank=False)
    text = models.TextField(null=False, blank=False)

    def __unicode__(self):
        return self.text[:20]


class ReadyCCO(ModelMixin):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    included_forms = models.ManyToManyField(BaseCCO, null=False, blank=False)

    def __unicode__(self):
        return '%s%s' % (self.unicode_prefex(), self.form_name)

    @property
    def name(self):
        return self.form_name


class CompletedCCO(ModelMixin):
    form_name = models.CharField(max_length=64, null=False, blank=False)
    form_data = JSONField(default={})

    def __unicode__(self):
        return '%s%s' % (self.unicode_prefex(), self.form_name)
