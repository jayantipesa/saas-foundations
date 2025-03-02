from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from django.contrib.auth import get_user_model
User = get_user_model()


@login_required
def profile_list_view(request):
    context = { 
        'object_list': User.objects.filter(is_active=True)
    }
    return render(request, 'profiles/list.html', context)


@login_required
def profile_detail_view(request, username=None, *args, **kwargs):
    user = request.user
    # user_groups = user.groups.all()
    # if user_groups.filter(name__icontains='basic').exists():
    #     return HttpResponse('Congrats')

    # print(user.has_perm('subscriptions.basic'),
    #       user.has_perm('subscriptions.basic_ai'),
    #       user.has_perm('subscriptions.pro'),
    #       user.has_perm('subscriptions.advanced'))
    
    if user.has_perm('subscriptions.basic_ai'):
        return HttpResponse('congrats, you have the basic AI plan enabled.')
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    context = {
        'object': profile_user_obj,
        'instance': profile_user_obj,
        'owner': is_me
    }

    return render(request, 'profiles/details.html', context)
