from django.contrib import admin
from django.forms.models import ModelForm

from sat_automations.manage_automations.models import ServiceAccount

# Admin Forms


class ServiceAccountForm(ModelForm):
    class Meta:
        model = ServiceAccount
        exclude = ["created_by"]


class ServiceAccountAdmin(admin.ModelAdmin):
    form = ServiceAccountForm

    list_display = ["service_name", "service_account_email", "created_by", "created", "modified"]

    def service_account_email(self, obj):
        return obj.service_account_data.get("client_email", "???")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user.email
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True


# Register your models here.
admin.site.register(ServiceAccount, ServiceAccountAdmin)
