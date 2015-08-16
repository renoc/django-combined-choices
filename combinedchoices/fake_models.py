from django.db import models

from combinedchoices.models import (
    BaseChoice as AbstractBaseChoice, BaseCCObj as AbstractBaseCCObj,
    ChoiceSection as AbstractChoiceSection, ReadyCombinedObj as AbsReady)


class BaseChoice(AbstractBaseChoice):
    pass


class BaseCCObj(AbstractBaseCCObj):
    pass


class ChoiceSection(AbstractChoiceSection):
    pass


class ReadyCombinedObj(AbsReady):
    pass
