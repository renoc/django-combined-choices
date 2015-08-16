from django.db import models

from combinedchoices.models import (
    BaseChoice as AbstractBaseChoice, BaseCCObj as AbstractBaseCCObj,
    ChoiceSection as AbstractChoiceSection)


class BaseChoice(AbstractBaseChoice):
    pass


class BaseCCObj(AbstractBaseCCObj):
    pass


class ChoiceSection(AbstractChoiceSection):
    pass
