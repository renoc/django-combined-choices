from django.contrib import admin
from combinedchoices.models import (
    BaseChoice, BaseCCObj, ChoiceField, Choice, CompletedCombinedObj,
    ReadyCombinedObj)


class ChoiceFieldThroughInline(admin.TabularInline):
    model = BaseCCObj.choice_fields.through


class BaseCCObjAdmin(admin.ModelAdmin):
    model = BaseCCObj
    inlines = (ChoiceFieldThroughInline,)


class ChoiceAdmin(admin.TabularInline):
    model = Choice


class ChoiceFieldAdmin(admin.ModelAdmin):
    model = ChoiceField
    inlines = [ChoiceAdmin,]
    list_display =['base_ccobj', 'base_choice']


admin.site.register(BaseChoice)
admin.site.register(BaseCCObj, BaseCCObjAdmin)
admin.site.register(ChoiceField, ChoiceFieldAdmin)
admin.site.register(CompletedCombinedObj)
admin.site.register(ReadyCombinedObj)
