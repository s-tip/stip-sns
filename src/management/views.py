import threading
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.http.response import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from ctirs.models import STIPUser, SNSConfig
from management.forms import SNSConfigForm
from feeds.mongo import Attck
from django.conf import settings as django_settings
from daemon.slack.receive import start_receive_slack_thread


@login_required
def user(request):
    ROLE_SELECT_KEY = 'role_select_'
    ROLE_SELECT_KEY_LENGTH = len('role_select_')
    user = request.user
    # 管理権限以外はエラー (403)
    if user.role != 'admin':
        return HttpResponseForbidden()

    # POST の場合はロール変更
    if request.method == 'POST':
        for key in request.POST:
            if not key.startswith(ROLE_SELECT_KEY):
                continue
            role = request.POST[key]
            user_id = int(key[ROLE_SELECT_KEY_LENGTH:])
            stip_user = STIPUser.objects.get(id=user_id)
            stip_user.role = role
            stip_user.save()
    users = STIPUser.objects.filter(is_active=True).order_by('username')
    return render(request, 'management/users.html', {'users': users})


def group(request):
    return


def check_port(port):
    if not isinstance(port, int):
        return False
    if port < 0 or port > 65535:
        return False
    return True


@login_required
def modify_attck_information(request):
    # 管理権限以外はエラー (403)
    if request.user.role != 'admin':
        return HttpResponseForbidden()
    # ATTCK 洗い替えと保存
    Attck.modify_save_attck_information()
    # その後は config 画面に遷移
    return sns_config(request)


@login_required
def reboot_slack_thread(request):
    # 管理権限以外はエラー (403)
    if request.user.role != 'admin':
        return HttpResponseForbidden()
    # thread 再起動
    start_receive_slack_thread()
    # その後は config 画面に遷移
    return sns_config(request)


@login_required
def sns_config(request):
    # 管理権限以外はエラー (403)
    if request.user.role != 'admin':
        return HttpResponseForbidden()
    sns_config = SNSConfig.objects.get()
    if request.method == 'POST':
        form = SNSConfigForm(request.POST)
        if form.is_valid():
            sns_config.common_cti_extractor_threat_actors_list = form.cleaned_data.get('common_cti_extractor_threat_actors_list')
            sns_config.common_cti_extractor_white_list = form.cleaned_data.get('common_cti_extractor_white_list')
            sns_config.sns_identity_name = form.cleaned_data.get('sns_identity_name')
            sns_config.sns_header_title = form.cleaned_data.get('sns_header_title')
            sns_config.sns_body_color = form.cleaned_data.get('sns_body_color')
            sns_config.sns_version_path = form.cleaned_data.get('sns_version_path')
            sns_config.sns_public_suffix_list_file_path = form.cleaned_data.get('sns_public_suffix_list_file_path')
            sns_config.circl_mongo_host = form.cleaned_data.get('circl_mongo_host')
            sns_config.circl_mongo_port = form.cleaned_data.get('circl_mongo_port')
            sns_config.circl_mongo_database = form.cleaned_data.get('circl_mongo_database')
            sns_config.attck_mongo_host = form.cleaned_data.get('attck_mongo_host')
            sns_config.attck_mongo_port = form.cleaned_data.get('attck_mongo_port')
            sns_config.attck_mongo_database = form.cleaned_data.get('attck_mongo_database')
            sns_config.cs_custid = form.cleaned_data.get('cs_custid')
            sns_config.cs_custkey = form.cleaned_data.get('cs_custkey')
            sns_config.rs_host = form.cleaned_data.get('rs_host')
            sns_config.rs_community_name = form.cleaned_data.get('rs_community_name')
            sns_config.gv_l2_url = form.cleaned_data.get('gv_l2_url')
            sns_config.jira_host = form.cleaned_data.get('jira_host')
            sns_config.jira_username = form.cleaned_data.get('jira_username')
            jira_password = form.cleaned_data.get('jira_password')
            if len(jira_password) != 0:
                sns_config.jira_password = jira_password
            sns_config.jira_project = form.cleaned_data.get('jira_project')
            sns_config.jira_type = form.cleaned_data.get('jira_type')
            sns_config.smtp_port = form.cleaned_data.get('smtp_port')
            sns_config.smtp_accept_mail_address = form.cleaned_data.get('smtp_accept_mail_address')
            sns_config.stix_ns_url = form.cleaned_data.get('stix_ns_url')
            sns_config.stix_ns_name = form.cleaned_data.get('stix_ns_name')
            sns_config.slack_bot_token = form.cleaned_data.get('slack_bot_token')
            sns_config.slack_bot_channel = form.cleaned_data.get('slack_bot_channel')
            if not check_port(sns_config.circl_mongo_port):
                messages.add_message(request,
                                     messages.WARNING,
                                     _('Mongo Port For Saving CVE Information From Circl.lu is invalid.'))
                return render(request, 'management/sns_config.html', {'form': form})
            if not check_port(sns_config.smtp_port):
                messages.add_message(request,
                                     messages.WARNING,
                                     _('SMTP Port is invalid.'))
                return render(request, 'management/sns_config.html', {'form': form})

            sns_config.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 _('SNS configuration was successfully edited.'))

    else:
        form = SNSConfigForm(instance=sns_config, initial={
            'common_cti_extractor_threat_actors_list': sns_config.common_cti_extractor_threat_actors_list,
            'common_cti_extractor_white_list': sns_config.common_cti_extractor_white_list,
            'sns_identity_name': sns_config.sns_identity_name,
            'sns_header_title': sns_config.sns_header_title,
            'sns_body_color': sns_config.sns_body_color,
            'sns_version_path': sns_config.sns_version_path,
            'sns_public_suffix_list_file_path': sns_config.sns_public_suffix_list_file_path,
            'circl_mongo_host': sns_config.circl_mongo_host,
            'circl_mongo_port': sns_config.circl_mongo_port,
            'circl_mongo_database': sns_config.circl_mongo_database,
            'attck_mongo_host': sns_config.attck_mongo_host,
            'attck_mongo_port': sns_config.attck_mongo_port,
            'attck_mongo_database': sns_config.attck_mongo_database,
            'cs_custid': sns_config.cs_custid,
            'cs_custkey': sns_config.cs_custkey,
            'rs_host': sns_config.rs_host,
            'rs_community_name': sns_config.rs_community_name,
            'gv_l2_url': sns_config.gv_l2_url,
            'jira_host': sns_config.jira_host,
            'jira_username': sns_config.jira_username,
            'jira_password': sns_config.jira_password,
            'jira_project': sns_config.jira_project,
            'jira_type': sns_config.jira_type,
            'smtp_port': sns_config.smtp_port,
            'smtp_accept_mail_address': sns_config.smtp_accept_mail_address,
            'stix_ns_url': sns_config.stix_ns_url,
            'stix_ns_name': sns_config.stix_ns_name,
            'slack_bot_token': sns_config.slack_bot_token,
            'slack_bot_channel': sns_config.slack_bot_channel,
        })

    return render(request, 'management/sns_config.html', {'form': form})
