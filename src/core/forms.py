import pytz
from django import forms
from ctirs.models import STIPUser as User
from django.utils.translation import ugettext_lazy as _
from ctirs.models import Region, Country, Profile
from stip.common.const import TLP_CHOICES, CRITICAL_INFRASTRUCTURE_CHOICES, LANGUAGES


class ProfileForm(forms.ModelForm):
    screen_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        label=_('Screen Name'),
        required=False)
    affiliation = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        label=_('affiliation'),
        required=False)
    job_title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        label=_('job_title'),
        required=False)
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=1024,
        label=_('URL'),
        required=False)
    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        label=_('location'),
        required=False)
    description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=1024,
        label=_('description'),
        required=False)
    tlp = forms.ChoiceField(
        choices=TLP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('TLP'),
        required=False)
    country = forms.ChoiceField(
        choices=Country.get_country_code_choices(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Country'),
        required=False)
    administrative_area = forms.ChoiceField(
        choices=Region.get_administrative_areas_choices('JP'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Administrative Area'),
        required=False)
    ci = forms.ChoiceField(
        choices=CRITICAL_INFRASTRUCTURE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Critical Infrastructure'),
        required=False)
    language = forms.ChoiceField(
        choices=LANGUAGES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Language'),
        required=True)
    scan_csv = forms.BooleanField(
        label=_('Scan CSV'),
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
        required=False)
    scan_pdf = forms.BooleanField(
        label=_('Scan PDF'),
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
        required=False)
    scan_post = forms.BooleanField(
        label=_('Scan Post'),
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
        required=False)
    scan_txt = forms.BooleanField(
        label=_('Scan TXT'),
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
        required=False)
    threat_actors = forms.CharField(
        label=_('Threat Actors'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'resize:none'}),
        required=False)
    indicator_white_list = forms.CharField(
        label=_('Indicator White List'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'resize:none'}),
        required=False)
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.all_timezones],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Timezone'),
        required=False)
    phantom_host = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Phantom Host'),
        required=False)
    phantom_source_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Phantom Source Name'),
        required=False)
    phantom_playbook_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Phantom Playbook Name'),
        required=False)
    phantom_auth_token = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Phantom Auth Token'),
        required=False)
    splunk_host = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Splunk Host'),
        required=False)
    splunk_api_port = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Splunk API Port'),
        required=False)
    splunk_web_port = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Splunk Web Port'),
        required=False)
    splunk_username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Splunk Username'),
        required=False)
    splunk_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Splunk Password'),
        required=False)
    splunk_scheme = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=Profile.SPLUNK_SCHEME_CHOICE,
        label=_('Splunk Scheme'),
        required=False)
    splunk_query = forms.CharField(
        label=_('Splunk Query'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'resize:none'}),
        required=False)

    class Meta:
        model = User
        fields = ['screen_name', 'affiliation', 'job_title',
                  'url', 'location', 'description', 'tlp', 'country', 'administrative_area',
                  'ci', 'language', 'scan_csv', 'scan_pdf', 'scan_post', 'scan_txt',
                  'threat_actors', 'indicator_white_list', 'timezone',
                  'phantom_host', 'phantom_source_name', 'phantom_playbook_name', 'phantom_auth_token',
                  'splunk_host', 'splunk_api_port', 'splunk_web_port', 'splunk_username', 'splunk_password', 'splunk_scheme', 'splunk_query']


class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_("Old password"),
        required=True)

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_("New password"),
        required=True)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_("Confirm new password"),
        required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')
        # id はSTIPUser id
        user = User.objects.get(pk=id)
        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class([
                'Old password don\'t match'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class([
                'Passwords don\'t match'])
        return self.cleaned_data
