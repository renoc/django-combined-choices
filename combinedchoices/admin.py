from django.contrib import admin
from combinedchoices.models import (
    BaseCCO, ChoiceSection, Choice, CompletedCCO, ReadyCCO, Section)


class ChoiceSectionThroughInline(admin.TabularInline):
    model = BaseCCO.sections.through


class BaseCCObjAdmin(admin.ModelAdmin):
    model = BaseCCO
    inlines = (ChoiceSectionThroughInline,)


class ChoiceAdmin(admin.TabularInline):
    model = Choice


class ChoiceSectionAdmin(admin.ModelAdmin):
    model = ChoiceSection
    inlines = [ChoiceAdmin,]
    list_display =['basecco', 'section']


admin.site.register(BaseCCO, BaseCCObjAdmin)
admin.site.register(ChoiceSection, ChoiceSectionAdmin)
admin.site.register(CompletedCCO)
admin.site.register(ReadyCCO)
admin.site.register(Section)
