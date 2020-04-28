from django.contrib import admin

from app.admin import StaticUrls as StaticUrls
from rules_engine.models.condition import Condition
from rules_engine.models.rule import Rule


class RuleConditionInline(admin.TabularInline):
    fields = ('field', 'value', 'content_type', 'operator',)
    model = Condition
    extra = 0


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    fields = ('tag', 'name', 'model', 'is_active', 'expiration', 'priority', 'halt', 'action', 'action_args',)
    list_display = ('tag', 'name', 'priority', 'is_active', 'expiration', )
    inlines = [RuleConditionInline]
    can_delete = False

    class Media:
        js = StaticUrls(
            "js/third_party/jquery-1.8.3.js",
            "js/admin/rules_engine.js"
        )
