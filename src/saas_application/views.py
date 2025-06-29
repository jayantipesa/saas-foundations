from django.shortcuts import render

from visits.models import PageVisit

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