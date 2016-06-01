from django import forms

from .models import QueryJob


class QueryJobForm(forms.ModelForm):
    class Meta:
        model = QueryJob
        fields = ('query', )
