# -*- coding: utf-8 -*-
import urlparse
import traceback
from django import template
from ctirs.models import Profile
register = template.Library()

#phanto に接続可能か?
@register.filter(name='can_connect_phantom')
def can_connect_phantom(sns_profile_id):
    try:
        profile = Profile.objects.get(id=sns_profile_id)
        if len(profile.phantom_host) == 0:
            return False
        if len(profile.phantom_source_name) == 0:
            return False
        if len(profile.phantom_playbook_name) == 0:
            return False
        if len(profile.phantom_auth_token) == 0:
            return False
        return True
    except Exception as _:
        traceback.print_exc()
        return False

#pk に含まれる . を -- に変更
@register.filter(name='get_accordion_pk')
def get_accordion_pk(v):
    return v.replace('.','--')

@register.filter(name='get_referred_url_tag')
def get_referred_url_tag(referred_url):
    url_parse = urlparse.urlparse(referred_url)
    if len(url_parse.scheme) == 0:
        url = referred_url
    else:
        url = '<a href="%s" target="_blank">%s</a>' % (referred_url,referred_url)
    return url
