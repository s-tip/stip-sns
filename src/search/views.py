import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from ctirs.models import Group, Feed, STIPUser as User
from feeds.views import extract_tags

try:
    from jira import JIRA
    imported_jira = True
except ImportError:
    imported_jira = False

FEEDS_NUM_PAGES = 10


@login_required
def search(request):
    if 'q' in request.GET:
        query_string = request.GET.get('q').strip()
        if len(query_string) == 0:
            return redirect('/search/')
        try:
            search_type = request.GET.get('type')
            if search_type not in ['feed', 'users']:
                search_type = 'feed'

        except Exception:
            search_type = 'feed'

        feeds = Feed.query(request.user, query_string, size=FEEDS_NUM_PAGES)

        if feeds:
            from_feed = feeds[0].package_id
        else:
            from_feed = None
    else:
        query_string = None
        feeds = []
        from_feed = None
    last_reload = str(datetime.datetime.now())
    users_list = User.objects.filter(is_active=True).exclude(username='anonymous').order_by('username')
    for i in range(len(feeds)):
        _, post = extract_tags(feeds[i].post)
        feeds[i].post = post
    r = render(request, 'search/search.html', {
        'feeds': feeds,
        'jira': imported_jira,
        'from_feed': from_feed,
        'last_reload': last_reload,
        'page': 1,
        'users': users_list,
        'sharing_groups': Group.objects.all(),
        'query_string': query_string,
    })
    r.set_cookie(key='username', value=str(request.user))
    return r
