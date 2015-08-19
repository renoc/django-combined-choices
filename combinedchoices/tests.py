from django.apps import apps
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import TestCase
from model_mommy import mommy

from combinedchoices.forms import ReadyForm
from combinedchoices.models import (
    BaseCCO, Choice, ChoiceSection, CompletedCCO, ReadyCCO, Section)


class Unicode_Tests(TestCase):

    def test_Section_Null(self):
        mod = mommy.make(Section, field_name='testbc')
        self.assertEqual('testbc', '%s' % mod)

    def test_Section_User(self):
        mod = mommy.make(
            Section, field_name='testuni', user__username='testuser')
        self.assertEqual('testuser - testuni', '%s' % mod)

    def test_BaseCCO_User(self):
        mod = mommy.make(
            BaseCCO, form_name='testuni', user__username='testuser')
        self.assertEqual('testuser - testuni', '%s' % mod)

    def test_BaseCCO_Null(self):
        mod = BaseCCO(form_name='testbcco')
        self.assertEqual('testbcco', '%s' % mod)

    def test_ChoiceSection(self):
        mod = mommy.make(
            ChoiceSection, basecco__form_name='testbcco',
            section__field_name='testbc')
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

    def test_ReadyCCO_Null(self):
        mod = ReadyCCO(form_name='testuni')
        self.assertEqual('testuni', '%s' % mod)

    def test_ReadyCCO_User(self):
        mod = mommy.make(
            ReadyCCO, form_name='testuni', user__username='testuser')
        self.assertEqual('testuser - testuni', '%s' % mod)


class BaseCCO_Tests(TestCase):

    def test_get_or_404(self):
        mod = BaseCCO.objects.create(form_name='testcc')
        self.assertEqual(BaseCCO.objects.get_or_404(id=mod.id), mod)
        self.assertRaises(Http404, BaseCCO.objects.get_or_404, id=99)

    def test_get_user_classes(self):
        user = User(username='testuser')
        user.save()
        mod = BaseCCO(form_name='testuni', user=user)
        mod.save()
        self.assertEqual(
            mod, BaseCCO.objects.get_user_objects(user=user).get())

    def test_name_property(self):
        testname = 'testname'
        mod = BaseCCO(form_name=testname)
        self.assertEqual(mod.name, testname)

    def test_name_property_combined(self):
        testname = 'testname'
        mod = ReadyCCO(form_name=testname)
        self.assertEqual(mod.name, testname)

    def test_unlinked_choices(self):
        user = mommy.make(User, username='testuser')
        tested = mommy.make(BaseCCO, form_name='tested', user=user)
        untested = mommy.make(BaseCCO, form_name='untested', user=user)
        modin = mommy.make(Section, field_name='in', user=user)
        modout = mommy.make(Section, field_name='out', user=user)
        modother = mommy.make(Section, field_name='other')
        mommy.make(ChoiceSection, basecco=tested, section=modin)
        mommy.make(ChoiceSection, basecco=untested, section=modout)
        self.assertEqual(tested.available_sections().get(), modout)


class Section_ModelTests(TestCase):

    def test_choice_text(self):
        mod = Section(field_type=1)
        self.assertEqual(mod.choice_type, 'Single')

    def test_linked_choices(self):
        mod = mommy.make(
            ChoiceSection, basecco__form_name='tested',
            section__field_name='modin')
        tested = mod.basecco
        modin = mod.section
        mod = mommy.make(
            ChoiceSection, basecco__form_name='untested',
            section__field_name='modout')
        self.assertNotEqual(tested, mod.basecco)
        self.assertNotEqual(modin, mod.section)
        self.assertEqual(tested.sections.get(), modin)

    def test_validate_pass(self):
        mod = mommy.make(Section, field_name='testuni')
        mod.save()
        mod.validate_unique()
        #No errors raised

    def test_validate_fail(self):
        mod = mommy.make(Section, field_name='testuni')
        mod.save()
        mod = mommy.make(Section, field_name='testuni')
        self.assertRaises(ValidationError, mod.validate_unique)


class ReadyForm_Tests(TestCase):

    def test_text_save(self):
        pass


class Section_Type_by_Form_Tests(TestCase):

    def test_character_form_init_cross(self):
        sect = mommy.make(
            Section, field_name='section', cross_combine=True,
            field_type=Section.MULTIPLE)
        comp1 = mommy.make(BaseCCO, form_name='test_compendium')
        cs = mommy.make(ChoiceSection, basecco=comp1, section=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)
        comp2 = mommy.make(BaseCCO, form_name='compendium_test')
        cs = mommy.make(ChoiceSection, basecco=comp2, section=sect)
        mommy.make(Choice, text='choice_test', choice_section=cs)
        combined = mommy.make(ReadyCCO, included_forms=[comp1])
        form = ReadyForm(ready_obj=combined)
        choices = form.fields['section'].widget.choices
        self.assertEqual(choices[0][1], 'test_choice')

    def test_character_form_init_uncross(self):
        sect = mommy.make(
            Section, field_name='section', cross_combine=False,
            field_type=Section.MULTIPLE)
        comp1 = mommy.make(BaseCCO, form_name='test_compendium')
        cs = mommy.make(ChoiceSection, basecco=comp1, section=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)
        comp2 = mommy.make(BaseCCO, form_name='compendium_test')
        cs = mommy.make(ChoiceSection, basecco=comp2, section=sect)
        mommy.make(Choice, text='choice_test', choice_section=cs)
        combined = mommy.make(ReadyCCO, included_forms=[comp1])
        form = ReadyForm(ready_obj=combined)
        choices = form.fields['test_compendium - section'].widget.choices
        self.assertEqual(choices[0][1], 'test_choice')

    def test_text_init(self):
        comp1 = mommy.make(BaseCCO, form_name='test_compendium')
        combined = mommy.make(ReadyCCO, included_forms=[comp1])
        kwargs = {'ready_obj': combined}
        form = ReadyForm(**kwargs)

        sect = mommy.make(
            Section, field_name='section', field_type=Section.TEXT)
        cs = mommy.make(ChoiceSection, basecco=comp1, section=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)

        self.assertEqual(len(form.fields), 1)
        form.create_section_field('name', sect, Choice.objects)
        self.assertEqual(len(form.fields), 2)
        self.assertEqual(form.fields['name'].initial, 'test_choice')

    def test_text_save(self):
        comp1 = mommy.make(BaseCCO, form_name='test_compendium')
        combined = mommy.make(ReadyCCO, included_forms=[comp1])
        kwargs = {'ready_obj': combined}

        sect = mommy.make(
            Section, field_name='section', field_type=Section.TEXT)
        cs = mommy.make(ChoiceSection, basecco=comp1, section=sect)
        mommy.make(Choice, text='test_choice', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': u'preset'}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertEqual(
            CompletedCCO.objects.get().form_data['section'][0], 'preset')

    def test_single_save(self):
        comp1 = mommy.make(BaseCCO, form_name='test_compendium')
        combined = mommy.make(ReadyCCO, included_forms=[comp1])
        kwargs = {'ready_obj': combined}

        sect = mommy.make(
            Section, field_name='section', field_type=Section.SINGLE)
        cs = mommy.make(ChoiceSection, basecco=comp1, section=sect)
        choice = mommy.make(Choice, text='preset', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': choice}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertEqual(
            CompletedCCO.objects.get().form_data['section'][0], 'preset')

    def test_description_save(self):
        comp1 = mommy.make(BaseCCO, form_name='test_compendium')
        combined = mommy.make(ReadyCCO, included_forms=[comp1])
        kwargs = {'ready_obj': combined}

        sect = mommy.make(
            Section, field_name='section', field_type=Section.DESCRIPTION)
        cs = mommy.make(ChoiceSection, basecco=comp1, section=sect)
        choice = mommy.make(Choice, text='preset', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': ''}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertFalse(
            'section' in CompletedCCO.objects.get().form_data.keys())

    def test_multiple_save(self):
        comp1 = mommy.make(BaseCCO, form_name='test_compendium')
        combined = mommy.make(ReadyCCO, included_forms=[comp1])
        kwargs = {'ready_obj': combined}

        sect = mommy.make(
            Section, field_name='section', field_type=Section.MULTIPLE)
        cs = mommy.make(ChoiceSection, basecco=comp1, section=sect)
        choice = mommy.make(Choice, text='test_choice', choice_section=cs)
        form = ReadyForm(**kwargs)
        form.cleaned_data = {'form_name': 'testcc', 'section': [choice]}

        self.assertFalse(CompletedCCO.objects.all().exists())

        form.save()

        self.assertTrue(CompletedCCO.objects.all().exists())
        self.assertEqual(
            CompletedCCO.objects.get().form_data['section'][0],
            choice.text)
