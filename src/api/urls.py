from django.contrib import admin
from django.urls import path
from api.v1.router import api
from django.shortcuts import redirect


def redirect_docs(request):
    return redirect('/api/docs')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('', redirect_docs)
]
