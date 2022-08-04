from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http.response import HttpResponseForbidden
from django.contrib import messages
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _
from ctirs.models import Group
from groups.forms import GroupForm
from ctirs.models import STIPUser


@login_required
def group(request):
    user = request.user
    # 管理権限以外はエラー (403)
    if not user.is_admin:
        return HttpResponseForbidden('You have no permission.')

    # POST の場合はロール変更
    if request.method == 'POST':
        pass
    groups = Group.objects.all()
    return render(request, 'groups/groups.html', {'groups': groups})


@login_required
def upsert(request):
    user = request.user
    # 管理権限以外はエラー (403)
    if not user.is_admin:
        return HttpResponseForbidden('You have no permission.')

    # (POST) upsert
    if request.method == 'POST':
        try:
            id_ = request.POST.get('id_')
            if len(id_) == 0:
                # id_ 指定なしの場合は新規作成
                group = Group()
                stip_user = request.user
                group.creator = stip_user
            else:
                # id_ 指定ありの場合はupdate (creator変更なし)
                group = Group.objects.get(id=int(id_))
            form = GroupForm(request.POST, instance=group)
            group.en_name = request.POST.get('en_name')
            group.local_name = request.POST.get('local_name')
            group.description = request.POST.get('description')
            if len(group.en_name) == 0:
                raise Exception(_('Fill Group Name (Common) Field.'))
            if len(group.local_name) == 0:
                raise Exception(_('Fill Group Name (Local) Field.'))
            group.locale = request.user.language
            group.save()
            # member 追加
            members = []
            for member_id in request.POST['members'].split(','):
                if len(member_id) == 0:
                    continue
                members.append(STIPUser.objects.get(id=member_id))
            group.members = members
            group.save()
            messages.add_message(request, messages.SUCCESS, _('Your Group was successfully edited.'))
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.add_message(request, messages.ERROR, str(e))
    # (GET)変更フォーム作成
    elif request.method == 'GET':
        # id_指定がない場合は新規作成
        if 'id_' not in request.GET:
            form = GroupForm()
        # id_指定がある場合はDBから初期状態取得
        else:
            id_ = int(request.GET['id_'])
            group = Group.objects.get(id=id_)
            member_list = []
            for member in group.members.all():
                member_list.append(str(member.id))
            form = GroupForm(instance=group, initial={
                'id_': id_,
                'en_name': group.en_name,
                'local_name': group.local_name,
                'description': group.description,
                'members': ','.join(member_list),
            })
    else:
        return HttpResponseForbidden()

    users = STIPUser.objects.filter(is_active=True).exclude(username='anonymous').order_by('username')
    return render(request, 'groups/upsert.html', {'form': form, 'users': users})


@login_required
def delete(request):
    # 管理権限以外はエラー (403)
    if not user.is_admin:
        return HttpResponseForbidden('You have no permission.')
    # 削除する Group ID
    id_ = int(request.GET['id_'])
    group = Group.objects.get(id=id_)
    group.delete()

    messages.add_message(request,
                         messages.SUCCESS,
                         _('Group was successfully deleted.'))
    groups = Group.objects.all()
    return render(request, 'groups/groups.html', {'groups': groups})
