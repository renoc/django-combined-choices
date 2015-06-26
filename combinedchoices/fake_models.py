from django.db import models

from combinedchoices.models import (
    BaseChoice as AbstractBaseChoice, BaseCCObj as AbstractBaseCCObj,
    Choice as AbstractChoice, ChoiceSection as AbstractChoiceSection,
    CompletedCombinedObj as AbsCompleted, ReadyCombinedObj as AbsReady)


class BaseChoice(AbstractBaseChoice):
    pass


class BaseCCObj(AbstractBaseCCObj):
    pass


class ChoiceSection(AbstractChoiceSection):
    pass


class Choice(AbstractChoice):
    pass


class ReadyCombinedObj(AbsReady):
    pass


class CompletedCombinedObj(AbsCompleted):
    pass
