from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from combinedchoices.fake_models import (
    BaseChoice, BaseCCObj, Choice, ChoiceSection, CompletedCombinedObj,
    ReadyCombinedObj)


class Unicode_Tests(TestCase):

    def test_BaseChoice(self):
        mod = mommy.make(BaseChoice, field_name='testbc')
        self.assertEqual('testbc', '%s' % mod)

    def test_BaseCCObj(self):
        mod = BaseCCObj(form_name='testbcco')
        self.assertEqual('testbcco', '%s' % mod)

    def test_ChoiceSection(self):
        mod = mommy.make(
            ChoiceSection, base_ccobj__form_name='testbcco',
            base_choice__field_name='testbc')
        self.assertEqual('testbcco - testbc', '%s' % mod)

    def test_Choice(self):
        mod = mommy.make(Choice, text='01234567890123456789twenty')
        self.assertEqual('%s' % mod, '01234567890123456789')

    def test_CompletedCombinedObj(self):
        mod = CompletedCombinedObj(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)

    def test_ReadyCombinedObj(self):
        mod = ReadyCombinedObj(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)


class BaseChoice_Tests(TestCase):

    def test_choice_text(self):
        mod = BaseChoice(field_type=1)
        self.assertEqual(mod.choice_type, 'Single')

    def test_linked_choices(self):
        hack = mommy.make(ChoiceSection, base_ccobj__form_name='hack')
        model = hack.base_ccobj.choice_sections.through
        mod = mommy.make(
            model, base_ccobj__form_name='tested',
            base_choice__field_name='modin')
        tested = mod.base_ccobj
        modin = mod.base_choice
        mod = mommy.make(
            model, base_ccobj__form_name='untested',
            base_choice__field_name='modout')
        self.assertNotEqual(tested, mod.base_ccobj)
        self.assertNotEqual(modin, mod.base_choice)
        self.assertEqual(tested.base_choices().get(), modin)

    def test_validate_pass(self):
        mod = BaseChoice(field_name='testuni', field_type=0)
        mod.save()
        mod.validate_unique()
        #No errors raised

    def test_validate_fail(self):
        mod = BaseChoice(field_name='testuni', field_type=0)
        mod.save()
        mod = BaseChoice(field_name='testuni', field_type=0)
        self.assertRaises(ValidationError, mod.validate_unique)
