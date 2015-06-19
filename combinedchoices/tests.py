from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from combinedchoices.models import (
    BaseChoice, BaseCCObj, ChoiceField, CompletedCombinedObj, ReadyCombinedObj)


class Unicode_Tests(TestCase):

    def call_BaseChoice(self):
        mod = mommy.make(BaseChoice, field_name='testbc')
        self.assertEqual('testbc', '%s' % mod)
        mod.save()
        return mod

    def call_BaseCCObj(self):
        mod = BaseCCObj(form_name='testbcco')
        self.assertEqual('testbcco', '%s' % mod)
        mod.save()
        return mod

    def test_ChoiceField(self):
        mod = ChoiceField(
            base_ccobj=self.call_BaseCCObj(),
            base_choice=self.call_BaseChoice())
        self.assertEqual('testbcco - testbc', '%s' % mod)

    def test_CompletedCombinedObj(self):
        mod = CompletedCombinedObj(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)

    def test_ReadyCombinedObj(self):
        mod = ReadyCombinedObj(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)


class BaseChoice_Tests(TestCase):

    def test_choice_text(self):
        mod = mommy.make(BaseChoice, field_type=1)
        self.assertEqual(mod.choice_type, 'Single')

    def test_linked_choices(self):
        tested = mommy.make(BaseCCObj, form_name='tested')
        untested = mommy.make(BaseCCObj, form_name='untested')
        modin = mommy.make(BaseChoice, field_name='in')
        modout = mommy.make(BaseChoice, field_name='out')
        mommy.make(ChoiceField, base_ccobj=tested, base_choice=modin)
        mommy.make(ChoiceField, base_ccobj=untested, base_choice=modout)
        self.assertEqual(tested.base_choices().get(), modin)

    def test_validate_pass(self):
        mod = mommy.make(BaseChoice, field_name='testuni')
        mod.save()
        mod.validate_unique()
        #No errors raised

    def test_validate_fail(self):
        mod = mommy.make(BaseChoice, field_name='testuni')
        mod.save()
        mod = mommy.make(BaseChoice, field_name='testuni')
        self.assertRaises(ValidationError, mod.validate_unique)
