from django.contrib.auth.decorators import login_required
from ctirs.models import STIPUser as User
from django.db.models import Q
from django.shortcuts import redirect, render
from ctirs.models import Feed


@login_required
def search(request):
    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()
        if len(querystring) == 0:
            return redirect('/search/')
        try:
            search_type = request.GET.get('type')
            if search_type not in ['feed', 'users']:
                search_type = 'feed'

        except Exception:
            search_type = 'feed'
        count = {}
        results = {}

        results['feed'] = Feed.query(request.user, querystring)
        results['users'] = User.objects.filter(
            Q(username__icontains=querystring)
            | Q(screen_name__icontains=querystring)
        )

        count['feed'] = len(results['feed'])
        count['users'] = results['users'].count()

        return render(request, 'search/results.html', {
            'hide_search': True,
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        })
    else:
        return render(request, 'search/search.html', {'hide_search': True})
