from django.contrib import admin
from combinedchoices.models import (
    BaseChoice, BaseCCObj, ChoiceSection, Choice, CompletedCCO, ReadyCCO)


class ChoiceSectionThroughInline(admin.TabularInline):
    model = BaseCCObj.choice_sections.through

    class Meta:
        abstract = True


class BaseCCObjAdmin(admin.ModelAdmin):
    model = BaseCCObj
    inlines = (ChoiceSectionThroughInline,)

    class Meta:
        abstract = True


class ChoiceAdmin(admin.TabularInline):
    model = Choice


class ChoiceSectionAdmin(admin.ModelAdmin):
    model = ChoiceSection
    inlines = [ChoiceAdmin,]
    list_display =['base_ccobj', 'base_choice']


#admin.site.register(BaseChoice)
#admin.site.register(BaseCCObj, BaseCCObjAdmin)
admin.site.register(ChoiceSection, ChoiceSectionAdmin)
admin.site.register(CompletedCCO)
admin.site.register(ReadyCCO)
