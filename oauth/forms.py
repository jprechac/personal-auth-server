from django import forms

from oauth import models


class ApplicationAdminCreationForm(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = [
            'name',
            'type',
        ]


