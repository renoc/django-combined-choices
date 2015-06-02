from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from combinedchoices.models import (
    BaseChoice, ReadyCombinedObj, BaseCCObj, CompletedCombinedObj)


class Unicode_Tests(TestCase):

    def test_BaseChoice(self):
        mod = BaseChoice(field_name='testuni')
        self.assertEqual('testuni', '%s' % mod)

    def test_ReadyCombinedObj(self):
        mod = ReadyCombinedObj(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)

    def test_BaseCCObj(self):
        mod = BaseCCObj(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)

    def test_CompletedCombinedObj(self):
        mod = CompletedCombinedObj(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)


class BaseChoice_Tests(TestCase):

    def test_validate_pass(self):
        mod = mommy.make(BaseChoice, field_name='testuni')
        mod.save()
        mod.validate_unique()
        #No errors raised

    def test_validate_fail(self):
        mod = mommy.make(BaseChoice, field_name='testuni')
        mod.save()
        mod = mommy.make(BaseChoice, field_name='testuni')
        self.assertRaises(ValidationError, mod.validate_unique())
