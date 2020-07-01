from django.contrib import admin

from oauth import forms
from oauth import models

# Register your models here.

@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name', 'type',),
        }),
        ("Access", {
            "fields": ('client_id', 'client_secret',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        }),
        ("Extras", {
            "fields": ('active', 'created_date', 'updated_date', 'id',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )

    # add_form = forms.ApplicationAdminCreationForm # TODO: make this work

    list_display = (
        'name',
        'type',
        'created_date',
        'active',
    )
    list_filter = (
        'type',
        'active',
        'created_date',
    )

    readonly_fields = [
        'client_id', 'client_secret',
        'created_date', 'updated_date',
        'id',
    ]

    # def get_form(self, request, obj=None, **kwargs):
    #     """
    #     Use special form during application creation
    #     """
    #     defaults = {}
    #     if obj is None:
    #         defaults['form'] = self.add_form
    #     defaults.update(kwargs)
    #     return super().get_form(request, obj, **defaults)


@admin.register(models.RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    pass

@admin.register(models.AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    pass

