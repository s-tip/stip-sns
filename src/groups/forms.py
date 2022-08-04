from django import forms
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _
from ctirs.models import Group


class GroupForm(forms.ModelForm):
    members = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)
    id_ = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)
    en_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('en_name'),
        required=True)
    local_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('local_name'),
        required=True)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        max_length=1024,
        label=_('description'),
        required=False)

    class Meta:
        model = Group
        fields = ['id_', 'en_name', 'local_name', 'description']
