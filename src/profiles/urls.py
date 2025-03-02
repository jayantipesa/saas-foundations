from django.urls import path, include

from .views import profile_detail_view, profile_list_view

urlpatterns = [
    path('', profile_list_view, name='profile_list'),
    path('<str:username>/', profile_detail_view, name='profile_detail_view')
]