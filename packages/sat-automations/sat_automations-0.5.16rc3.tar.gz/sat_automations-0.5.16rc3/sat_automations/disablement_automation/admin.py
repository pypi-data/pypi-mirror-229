from django.contrib import admin  # noqa: F401

from sat_automations.disablement_automation.models import DisablementLog


class DisablementLogAdmin(admin.ModelAdmin):
    list_display = [
        "campus_id",
        "status",
        "message",
        "has_extra_info",
        "created",
    ]
    readonly_fields = [
        "campus_id",
        "status",
        "message",
        "extra_info",
        "created",
    ]
    search_fields = ["campus_id"]
    list_filter = ["status", "message", "created"]

    class Meta:
        model = DisablementLog

    def has_module_permission(self, request, obj=None):
        if not request.user.is_staff:
            return False
        return True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_extra_info(self, obj):
        return obj.extra_info is not None

    has_extra_info.boolean = True


# Register your models here.
admin.site.register(DisablementLog, DisablementLogAdmin)
