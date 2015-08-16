from django.db import models

from combinedchoices.models import (
    BaseChoice as AbstractBaseChoice, BaseCCObj as AbstractBaseCCObj)


class BaseChoice(AbstractBaseChoice):
    pass


class BaseCCObj(AbstractBaseCCObj):
    pass
