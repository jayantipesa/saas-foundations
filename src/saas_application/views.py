from django.shortcuts import render

from visits.models import PageVisit

def home_view(request, *args, **kwargs):
    page_visit_qs = PageVisit.objects.filter(path=request.path)
    context = {
        'name': 'Jayanti',
        'page_visit_count': page_visit_qs.count()
    }
    PageVisit.objects.create(path=request.path)
    return render(request, 'home.html', context=context)