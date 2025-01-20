from django.urls import path, re_path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        re_path(r'^pattern$', views.pattern, name='pattern'),
        re_path(r'^preview$', views.preview, name='preview'),
        re_path(r'^check_fit$', views.check_fit, name='check_fit'),
        re_path(r'^check_progress$', views.check_progress, name='check_progress'),
]
