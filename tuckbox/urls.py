from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('pattern', views.pattern, name='pattern'),
        path('preview', views.preview),
        path('check_fit', views.check_fit)
]
