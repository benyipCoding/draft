from django.urls import re_path

from .views import PersonViewSet, MovieViewSet

urlpatterns = [
    re_path(r"^person/(?:(?P<uid>.+)/?)?$", PersonViewSet.as_view()),
    re_path(r"^movie/(?:(?P<uid>.+)/?)?$", MovieViewSet.as_view()),
]
