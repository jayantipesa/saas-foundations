from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from visits.models import PageVisit

LOGIN_URL = settings.LOGIN_URL


def home_view(request, *args, **kwargs):
    return about_view(request, *args, **kwargs)


def about_view(request, *args, **kwargs):
    all_page_visit_qs = PageVisit.objects.all()
    page_visit_count = all_page_visit_qs.filter(path=request.path).count()
    try:
        count_percentage = (page_visit_count * 100.0) / all_page_visit_qs.count()
    except:
        count_percentage = 0
    context = {
        'name': 'Jayanti',
        'total_page_visit_count': all_page_visit_qs.count(),
        'page_visit_count': page_visit_count,
        'percentage': round(count_percentage, 0)
    }
    PageVisit.objects.create(path=request.path)
    return render(request, 'home.html', context=context)


def pw_protected_view(request, *args, **kwargs):
    one_time_password = 'abc123'
    is_allowed = request.session.get('protected_page_allowed') or 0
    if request.method == 'POST':
        user_pw_sent = request.POST.get('code') or None
        if not request.user.is_authenticated:
            if user_pw_sent == one_time_password:
                return render(request, 'protected/view.html', {})
        else:
            is_valid = request.user.check_password(user_pw_sent)
            if is_valid:
                is_allowed = 1
                request.session['protected_page_allowed'] = is_allowed
    if is_allowed:
        return render(request, 'protected/view.html', {})
    return render(request, 'protected/entry.html', {})


@login_required(login_url=LOGIN_URL)
def user_only_view(request, *args, **kwargs):
    return render(request, 'protected/user-only.html', {})


@staff_member_required
def staff_only_view(request, *args, **kwargs):
    return render(request, 'protected/user-only.html', {})