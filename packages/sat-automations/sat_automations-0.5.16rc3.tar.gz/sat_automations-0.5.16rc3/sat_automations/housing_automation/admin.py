from datetime import datetime, timedelta

from django.contrib import admin  # noqa: F401

from sat_automations.housing_automation.models import (
    AssignRevokeLog,
    AssignRevokeTracker,
    Clearance,
    RoomUseCode,
)

# Custom ListFilters


class TrackerNullFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "Status"

    def lookups(self, request, model_admin):
        return ("null", "Not Processed"), ("not_null", "Processed")

    def queryset(self, request, queryset):
        if self.value() == "null":
            return queryset.filter(status__isnull=True)
        if self.value() == "not_null":
            return queryset.filter(status__isnull=False)


class TrackerDateFilterBase(admin.SimpleListFilter):
    delta_plus_three = (datetime.now() + timedelta(days=3)).date()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    now = datetime.now().date()

    def lookups(self, request, model_admin):
        return (
            ("yesterday", "Yesterday"),
            ("today", "Today"),
            ("tomorrow", "Tomorrow"),
            ("next_three_days", "Within Next Three Days"),
        )


class MoveInFilter(TrackerDateFilterBase):
    title = "Move In Date"
    parameter_name = "move_in_date"

    def queryset(self, request, queryset):
        if self.value() == "next_three_days":
            return queryset.filter(
                move_in_date__gte=self.now, move_in_date__lte=self.delta_plus_three
            )
        if self.value() == "yesterday":
            return queryset.filter(move_in_date=self.yesterday)
        if self.value() == "today":
            return queryset.filter(move_in_date=self.now)
        if self.value() == "tomorrow":
            return queryset.filter(move_in_date=self.tomorrow)


class MoveOutFilter(TrackerDateFilterBase):
    title = "Move Out Date"
    parameter_name = "move_out_date"

    def queryset(self, request, queryset):
        if self.value() == "next_three_days":
            return queryset.filter(
                move_out_date__gte=self.now, move_out_date__lte=self.delta_plus_three
            )
        if self.value() == "yesterday":
            return queryset.filter(move_out_date=self.yesterday)
        if self.value() == "today":
            return queryset.filter(move_out_date=self.now)
        if self.value() == "tomorrow":
            return queryset.filter(move_out_date=self.tomorrow)


class AssignRevokeLogAdmin(admin.ModelAdmin):
    list_display = [
        "building_code",
        "campus_id",
        "clearance_type",
        "status",
        "message",
        "has_extra_info",
        "created",
    ]
    readonly_fields = [
        "building_code",
        "campus_id",
        "clearance_type",
        "status",
        "message",
        "extra_info",
        "created",
    ]
    search_fields = ["building_code", "campus_id"]
    list_filter = ["clearance_type", "status", "message", "created"]

    class Meta:
        model = AssignRevokeLog

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


class AssignRevokeTrackerAdmin(admin.ModelAdmin):
    list_display = [
        "campus_id",
        "building_code",
        "move_in_date",
        "move_out_date",
        "status",
        "created",
        "modified",
    ]
    readonly_fields = [
        "campus_id",
        "building_code",
        "move_in_date",
        "move_out_date",
        "status",
        "created",
        "modified",
    ]
    search_fields = ["building_code", "campus_id"]
    list_filter = ["status", "created", MoveInFilter, MoveOutFilter, TrackerNullFilter]

    class Meta:
        model = AssignRevokeTracker

    def has_module_permission(self, request, obj=None):
        if not request.user.is_staff:
            return False
        return True


class RoomUseCodeAdmin(admin.ModelAdmin):
    list_display = ["name", "clearance", "created", "modified"]
    list_filter = ["clearance", "created", "modified"]

    ordering = ["name"]
    search_fields = ["name"]

    class Meta:
        model = RoomUseCode


class ClearanceAdmin(admin.ModelAdmin):
    list_display = ["name", "created", "modified"]
    list_filter = ["name", "created", "modified"]

    ordering = ["name"]
    search_fields = ["name"]

    class Meta:
        model = Clearance


# Register your models here.
admin.site.register(AssignRevokeLog, AssignRevokeLogAdmin)
admin.site.register(AssignRevokeTracker, AssignRevokeTrackerAdmin)
admin.site.register(Clearance, ClearanceAdmin)
admin.site.register(RoomUseCode, RoomUseCodeAdmin)
