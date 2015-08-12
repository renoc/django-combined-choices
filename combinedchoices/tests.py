from django.apps import apps
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from combinedchoices.models import BASE_MODEL, SECTION_MODEL, THROUGH_MODEL, CompletedCCO
from combinedchoices.fake_models import ReadyCombinedObj
from combinedchoices.forms import ReadyForm, CHOICE_MODEL


BaseCCObj = apps.get_model(*BASE_MODEL.split('.'))
BaseChoice = apps.get_model(*SECTION_MODEL.split('.'))
Choice = apps.get_model(*CHOICE_MODEL.split('.'))
ChoiceSection = apps.get_model(*THROUGH_MODEL.split('.'))


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

    def test_CompletedCCO_Null(self):
        mod = CompletedCCO(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)

    def test_CompletedCCO_User(self):
        mod = mommy.make(
            CompletedCCO, form_name='testuni', user__username='testuser')
        self.assertEqual('testuser - testuni', '%s' % mod)

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

# Validate overwritten in front end repo
#    def test_validate_fail(self):
#        mod = BaseChoice(field_name='testuni', field_type=0)
#        mod.save()
#        mod = BaseChoice(field_name='testuni', field_type=0)
#        self.assertRaises(ValidationError, mod.validate_unique)


class ReadyForm_Tests(TestCase):

    def test_text_save(self):
        pass


class Section_Type_by_Form_Tests(TestCase):

    def test_character_form_init_cross(self):
        sect = mommy.make(
            BaseChoice, field_name='section', cross_combine=True,
            field_type=BaseChoice.MULTIPLE)
        comp1 = mommy.make(BaseCCObj, form_name='test_compendium')
        cs = mommy.make(ChoiceSection, base_ccobj=comp1, base_choice=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)
        comp2 = mommy.make(BaseCCObj, form_name='compendium_test')
        cs = mommy.make(ChoiceSection, base_ccobj=comp2, base_choice=sect)
        mommy.make(Choice, text='choice_test', choice_section=cs)
        combined = mommy.make(ReadyCombinedObj, included_forms=[comp1])
        form = ReadyForm(ready_class=combined)
        choices = form.fields['section'].widget.choices
        self.assertEqual(choices[0][1], 'test_choice')

    def test_character_form_init_uncross(self):
        sect = mommy.make(
            BaseChoice, field_name='section', cross_combine=False,
            field_type=BaseChoice.MULTIPLE)
        comp1 = mommy.make(BaseCCObj, form_name='test_compendium')
        cs = mommy.make(ChoiceSection, base_ccobj=comp1, base_choice=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)
        comp2 = mommy.make(BaseCCObj, form_name='compendium_test')
        cs = mommy.make(ChoiceSection, base_ccobj=comp2, base_choice=sect)
        mommy.make(Choice, text='choice_test', choice_section=cs)
        combined = mommy.make(ReadyCombinedObj, included_forms=[comp1])
        form = ReadyForm(ready_class=combined)
        choices = form.fields['test_compendium - section'].widget.choices
        self.assertEqual(choices[0][1], 'test_choice')

    def test_text_init(self):
        comp1 = mommy.make(BaseCCObj, form_name='test_compendium')
        combined = mommy.make(ReadyCombinedObj, included_forms=[comp1])
        kwargs = {'ready_class': combined}
        form = ReadyForm(**kwargs)

        sect = mommy.make(
            BaseChoice, field_name='section', field_type=BaseChoice.TEXT)
        cs = mommy.make(ChoiceSection, base_ccobj=comp1, base_choice=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)

        self.assertEqual(len(form.fields), 1)
        form.create_section_field('name', sect, Choice.objects)
        self.assertEqual(len(form.fields), 2)
        self.assertEqual(form.fields['name'].initial, 'test_choice')

    def test_text_save(self):
        comp1 = mommy.make(BaseCCObj, form_name='test_compendium')
        combined = mommy.make(ReadyCombinedObj, included_forms=[comp1])
        kwargs = {'ready_class': combined}

        sect = mommy.make(
            BaseChoice, field_name='section', field_type=BaseChoice.TEXT)
        cs = mommy.make(ChoiceSection, base_ccobj=comp1, base_choice=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': u'preset'}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertEqual(
            CompletedCCO.objects.get().form_data['section'][0], 'preset')

    def test_single_save(self):
        comp1 = mommy.make(BaseCCObj, form_name='test_compendium')
        combined = mommy.make(ReadyCombinedObj, included_forms=[comp1])
        kwargs = {'ready_class': combined}

        sect = mommy.make(
            BaseChoice, field_name='section', field_type=BaseChoice.SINGLE)
        cs = mommy.make(ChoiceSection, base_ccobj=comp1, base_choice=sect)
        choice = mommy.make(Choice, text='preset', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': choice}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertEqual(
            CompletedCCO.objects.get().form_data['section'][0], 'preset')

    def test_description_save(self):
        comp1 = mommy.make(BaseCCObj, form_name='test_compendium')
        combined = mommy.make(ReadyCombinedObj, included_forms=[comp1])
        kwargs = {'ready_class': combined}

        sect = mommy.make(
            BaseChoice, field_name='section', field_type=BaseChoice.DESCRIPTION)
        cs = mommy.make(ChoiceSection, base_ccobj=comp1, base_choice=sect)
        choice = mommy.make(Choice, text='preset', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': ''}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertFalse(
            'section' in CompletedCCO.objects.get().form_data.keys())

    def test_multiple_save(self):
        comp1 = mommy.make(BaseCCObj, form_name='test_compendium')
        combined = mommy.make(ReadyCombinedObj, included_forms=[comp1])
        kwargs = {'ready_class': combined}

        sect = mommy.make(
            BaseChoice, field_name='section', field_type=BaseChoice.MULTIPLE)
        cs = mommy.make(ChoiceSection, base_ccobj=comp1, base_choice=sect)
        choice = mommy.make(Choice, text='test_choice', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': [choice]}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertEqual(
            CompletedCCO.objects.get().form_data['section'][0],
            choice.text)
