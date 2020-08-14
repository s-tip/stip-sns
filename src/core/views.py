import io
import os
import json
import qrcode
import base64
import pyotp

from PIL import Image
from decorators import ajax_required
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http.response import HttpResponse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
import stip.common.login as login_views
from stip.common.login import set_language_setting
from ctirs.models import STIPUser as User
from core.forms import ChangePasswordForm, ProfileForm
from ctirs.models import Region, Feed
from ctirs.models.rs.models import STIPUser
from feeds.views import FEEDS_NUM_PAGES, feeds

DEFAULT_COUNTRY = 'JP'
DEFAULT_CODE = 'JP-13'

REDIRECT_TO = 'feeds'


def login(request):
    return login_views.login(request, REDIRECT_TO)


def login_totp(request):
    return login_views.login_totp(request, REDIRECT_TO)


def home(request):
    if request.user.is_authenticated():
        stip_user = request.user
        request = set_language_setting(request, stip_user)
        return feeds(request)
    else:
        lang = 'en'
        request.session['_language'] = lang
        translation.activate(lang)
        return render(request, 'cover.html')


@login_required
def network(request):
    users_list = User.objects.filter(is_active=True).order_by('username')
    paginator = Paginator(users_list, 100)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(request, 'core/network.html', {'users': users})


@login_required
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    feeds = Feed.get_feeds(
        api_user=request.user,
        user_id=page_user.id,
        index=0,
        size=FEEDS_NUM_PAGES)

    from_feed = None
    if feeds:
        from_feed = feeds[0].package_id
    return render(request, 'core/profile.html', {
        'page_user': page_user,
        'feeds': feeds,
        'from_feed': from_feed,
        'page': 1
    })


@login_required
def settings(request):
    stip_user = request.user
    profile = stip_user.sns_profile
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        country = request.POST['country']
        form.fields['administrative_area'].choices = Region.get_administrative_areas_choices(country)
        if form.is_valid():
            stip_user.screen_name = form.cleaned_data.get('screen_name')
            stip_user.timezone = form.cleaned_data.get('timezone')
            stip_user.affiliation = form.cleaned_data.get('affiliation')
            stip_user.job_title = form.cleaned_data.get('job_title')
            stip_user.url = form.cleaned_data.get('url')
            stip_user.location = form.cleaned_data.get('location')
            stip_user.description = form.cleaned_data.get('description')
            stip_user.tlp = form.cleaned_data.get('tlp')
            code = form.cleaned_data.get('administrative_area')
            try:
                region = Region.objects.get(code=code)
                administraive_code = region.code
                administraive_area = region.administrative_area
                country_code = region.country_code
            except BaseException:
                region = None
                administraive_code = None
                administraive_area = None
                country_code = form.cleaned_data.get('country')
            stip_user.region = region
            stip_user.administrative_code = administraive_code
            stip_user.administrative_area = administraive_area
            stip_user.country_code = country_code
            stip_user.ci = form.cleaned_data.get('ci')
            stip_user.language = form.cleaned_data.get('language')
            profile.scan_csv = form.cleaned_data.get('scan_csv')
            profile.scan_pdf = form.cleaned_data.get('scan_pdf')
            profile.scan_post = form.cleaned_data.get('scan_post')
            profile.scan_txt = form.cleaned_data.get('scan_txt')
            profile.threat_actors = form.cleaned_data.get('threat_actors')
            profile.indicator_white_list = form.cleaned_data.get('indicator_white_list')
            profile.phantom_host = form.cleaned_data.get('phantom_host')
            profile.phantom_source_name = form.cleaned_data.get('phantom_source_name')
            profile.phantom_playbook_name = form.cleaned_data.get('phantom_playbook_name')
            phantom_auth_token = form.cleaned_data.get('phantom_auth_token')
            if len(phantom_auth_token) != 0:
                profile.phantom_auth_token = form.cleaned_data.get('phantom_auth_token')
            profile.splunk_host = form.cleaned_data.get('splunk_host')
            profile.splunk_api_port = form.cleaned_data.get('splunk_api_port')
            profile.splunk_web_port = form.cleaned_data.get('splunk_web_port')
            profile.splunk_username = form.cleaned_data.get('splunk_username')
            splunk_password = form.cleaned_data.get('splunk_password')
            if len(splunk_password) != 0:
                profile.splunk_password = splunk_password
            profile.splunk_scheme = form.cleaned_data.get('splunk_scheme')
            profile.splunk_query = form.cleaned_data.get('splunk_query')
            stip_user.save()
            profile.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 _('Your profile was successfully edited.'))
            lang = stip_user.language
            translation.activate(lang)
            request.session['_language'] = lang
    else:
        if stip_user.region is None:
            country = stip_user.country_code
            code = ''
        else:
            country = stip_user.region.country_code
            code = stip_user.region.code
        form = ProfileForm(instance=profile, initial={
            'screen_name': stip_user.screen_name,
            'affiliation': stip_user.affiliation,
            'job_title': stip_user.job_title,
            'url': stip_user.url,
            'location': stip_user.location,
            'description': stip_user.description,
            'tlp': stip_user.tlp,
            'country': country,
            'administrative_area': code,
            'ci': stip_user.ci,
            'language': stip_user.language,
            'scan_csv': profile.scan_csv,
            'scan_pdf': profile.scan_pdf,
            'scan_post': profile.scan_post,
            'scan_txt': profile.scan_txt,
            'threat_actors': profile.threat_actors,
            'indicator_white_list': profile.indicator_white_list,
            'timezone': stip_user.timezone,
            'phantom_host': profile.phantom_host,
            'phantom_source_name': profile.phantom_source_name,
            'phantom_playbook_name': profile.phantom_playbook_name,
            'phantom_auth_token': profile.phantom_auth_token,
            'splunk_host': profile.splunk_host,
            'splunk_api_port': profile.splunk_api_port,
            'splunk_web_port': profile.splunk_web_port,
            'splunk_username': profile.splunk_username,
            'splunk_password': profile.splunk_password,
            'splunk_scheme': profile.splunk_scheme,
            'splunk_query': profile.splunk_query,
        })
        form.fields['administrative_area'].choices = Region.get_administrative_areas_choices(country)

    return render(request, 'core/settings.html', {'form': form})


@login_required
def picture(request):
    uploaded_picture = False
    try:
        if request.GET.get('upload_picture') == 'uploaded':
            uploaded_picture = True

    except Exception:
        pass

    return render(request, 'core/picture.html',
                  {'uploaded_picture': uploaded_picture})


@login_required
def password(request, msg=None):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            if user.username == 'admin':
                User.change_build_password(new_password)
            user.is_modified_password = True
            user.save()
            update_session_auth_hash(request, user)
            messages.add_message(request, messages.SUCCESS,
                                 'Your password was successfully changed.')
            return redirect('password')

    else:
        u = STIPUser.objects.get(username=user)
        flg_enable_2fa = False
        if u.totp_secret is not None:
            flg_enable_2fa = True
        form = ChangePasswordForm(
            instance=user,
            initial={'enable_2fa': flg_enable_2fa}
        )
    return render(request, 'core/password.html', {'form': form, 'password_msg': msg})


@login_required
def password_modified(request, msg=None):
    user = request.user
    form = ChangePasswordForm(instance=user)
    return render(request, 'core/password.html', {'form': form, 'password_msg': 'Please Change Your Password!!!'})


@login_required
def upload_picture(request):
    try:
        profile_pictures = django_settings.MEDIA_ROOT + '/profile_pictures/'
        if not os.path.exists(profile_pictures):
            os.makedirs(profile_pictures)
        f = request.FILES['picture']
        filename = profile_pictures + request.user.username + '_tmp.jpg'
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        im = Image.open(filename)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        width, height = im.size
        if width > 350:
            new_width = 350
            new_height = (height * 350) / width
            new_size = new_width, new_height
            im.thumbnail(new_size, Image.ANTIALIAS)
            im.save(filename)

        return redirect('/settings/picture/?upload_picture=uploaded')

    except Exception as e:
        print(e)
        return redirect('/settings/picture/')


@login_required
def save_uploaded_picture(request):
    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        w = int(request.POST.get('w'))
        h = int(request.POST.get('h'))
        tmp_filename = django_settings.MEDIA_ROOT + '/profile_pictures/' +\
            request.user.username + '_tmp.jpg'
        filename = django_settings.MEDIA_ROOT + '/profile_pictures/' +\
            request.user.username + '.jpg'
        im = Image.open(tmp_filename)
        cropped_im = im.crop((x, y, w + x, h + y))
        cropped_im.thumbnail((200, 200), Image.ANTIALIAS)
        if cropped_im.mode != 'RGB':
            cropped_im = cropped_im.convert('RGB')
        cropped_im.save(filename)
        os.remove(tmp_filename)

    except Exception as e:
        print(e)
        return redirect('/settings/picture/')

    return redirect('/settings/picture/')


@ajax_required
def get_administrative_area(request):
    country_code = request.GET.get('country_code')
    dump = []
    for item in Region.get_administrative_areas(country_code):
        d = {}
        d['administraive_area'] = ugettext(item.administrative_area)
        d['code'] = item.code
        dump.append(d)
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')


@login_required
@ajax_required
def get_2fa_secet(request):
    stip_user = str(request.user)
    base32secet = pyotp.random_base32()
    otp = pyotp.totp.TOTP(base32secet)
    uri = otp.provisioning_uri(name=stip_user, issuer_name="S-TIP")

    qr = qrcode.make(uri)
    img = io.BytesIO()
    qr.save(img)
    base64_img = base64.b64encode(img.getvalue()).decode()

    request.session['secet'] = base32secet
    request.session['user'] = stip_user

    d = {}
    d['qrcode'] = base64_img
    d['secet'] = base32secet
    data = json.dumps(d)
    return HttpResponse(data, content_type='application/json')


@login_required
@ajax_required
def enable_2fa(request):
    secet = request.session['secet']
    stip_user = request.session['user']
    totp = pyotp.TOTP(secet)
    authentication_code = request.POST.get('authentication_code')

    d = {}
    if totp.verify(authentication_code):
        u = STIPUser.objects.get(username=stip_user)
        u.totp_secret = secet
        u.save()
        d = {
            "status": "OK"
        }
    else:
        d = {
            "status": "NG",
            "error_msg": "The authorization code is incorrect."
        }
    data = json.dumps(d)
    return HttpResponse(data, content_type='application/json')


@login_required
@ajax_required
def disable_2fa(request):
    user = str(request.user)
    u = STIPUser.objects.get(username=user)
    u.totp_secret = None
    u.save()
    d = {
        "status": "OK"
    }
    data = json.dumps(d)
    return HttpResponse(data, content_type='application/json')
