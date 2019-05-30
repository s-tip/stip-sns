# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from ctirs.models import SNSConfig

class SNSConfigForm(forms.ModelForm):
    common_cti_extractor_threat_actors_list = forms.CharField(
        label = _('Common Threat Actors List'),
        widget=forms.Textarea(attrs={'class':'form-control','style':'resize:none'}),
        required=False)
    common_cti_extractor_white_list = forms.CharField(
        label = _('Common CTI Extractor White List'),
        widget=forms.Textarea(attrs={'class':'form-control','style':'resize:none'}),
        required=False)
    sns_identity_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=32,
        label=_('Identity Name'),
        required=True)
    sns_header_title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=32,
        label=_('Header Title'),
        required=True)
    sns_body_color = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=32,
        label=_('Body Color'),
        required=True)
    sns_version_path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=1024,
        label=_('Version File Path'),
        required=True)
    sns_public_suffix_list_file_path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=1024,
        label=_('Public Suffix List File Path'),
        required=True)
    circl_mongo_host = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Mongo Host For Saving CVE Information From Circl.lu'),
        required=True)
    circl_mongo_port = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Mongo Port For Saving CVE Information From Circl.lu'),
        required=True)
    circl_mongo_database = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('Mongo Database For Saving CVE Information From Circl.lu'),
        required=True)
    attck_mongo_host = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Mongo Host For Saving Attacker Information From ATT&CK'),
        required=True)
    attck_mongo_port = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Mongo Port For Saving Attacker Information From ATT&CK'),
        required=True)
    attck_mongo_database = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('Mongo Database For Saving Attacker Information From ATT&CK'),
        required=True)
    cs_custid = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('X-CSIX-CUSTID for CrowdStrikeAPI'),
        required=False)
    cs_custkey = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('X-CSIX-CUSTkEY for CrowdStrikeAPI'),
        required=False)
    rs_host = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('RS HOST Which Save SNS STIX'),
        required=True)
    rs_community_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('Community Name of RS Which Save SNS STIX'),
        required=True)
    proxy_http = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Proxy URL for http'),
        required=False)
    proxy_https = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Proxy URL for https'),
        required=False)
    gv_l2_url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('GraphView URL'),
        required=False)
    jira_host = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('JIRA Host'),
        required=False)
    jira_username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('JIRA Username'),
        required=False)
    jira_password = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('JIRA Password'),
        required=False)
    jira_project = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('JIRA Project'),
        required=False)
    jira_type = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=64,
        label=_('JIRA Type'),
        required=False)
    smtp_port = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('SMTP port'),
        required=False)
    smtp_accept_mail_address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('SMTP Accept Mail address'),
        required=False)
    stix_ns_url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('STIX Namespace URL'),
        required=True)
    stix_ns_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('STIX Namespace Name'),
        required=True)
    slack_bot_token = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Slack Bot Token'),
        required=False)
    slack_bot_channel = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=128,
        label=_('Slack Bot Channel'),
        required=False)


    class Meta:
        model = SNSConfig
        fields = ['common_cti_extractor_threat_actors_list','common_cti_extractor_white_list',
                  'sns_identity_name', 'sns_header_title', 'sns_body_color', 'sns_version_path', 'sns_public_suffix_list_file_path',
                  'circl_mongo_host', 'circl_mongo_port', 'circl_mongo_database',
                  'attck_mongo_host', 'attck_mongo_port', 'attck_mongo_database',
                  'cs_custid','cs_custkey',
                  'rs_host','rs_community_name',
                  'proxy_http','proxy_https','gv_l2_url',
                  'jira_host','jira_username','jira_password','jira_project','jira_type',
                  'smtp_port', 'smtp_accept_mail_address',
                  'stix_ns_url', 'stix_ns_name', 'slack_bot_token', 'slack_bot_channel']

