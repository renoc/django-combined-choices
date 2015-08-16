from django.contrib import admin
from combinedchoices.models import (
    BaseCCO, ChoiceSection, Choice, CompletedCCO, ReadyCCO, Section)


class ChoiceSectionThroughInline(admin.TabularInline):
    model = BaseCCO.choice_sections.through

    class Meta:
        abstract = True


class BaseCCObjAdmin(admin.ModelAdmin):
    model = BaseCCO
    inlines = (ChoiceSectionThroughInline,)

    class Meta:
        abstract = True


class ChoiceAdmin(admin.TabularInline):
    model = Choice


class ChoiceSectionAdmin(admin.ModelAdmin):
    model = ChoiceSection
    inlines = [ChoiceAdmin,]
    list_display =['base_ccobj', 'base_choice']


admin.site.register(BaseCCO, BaseCCObjAdmin)
admin.site.register(ChoiceSection, ChoiceSectionAdmin)
admin.site.register(CompletedCCO)
admin.site.register(ReadyCCO)
admin.site.register(Section)
