# coding=utf-8
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^fpms/', include('fpms.urls', namespace='fpms'))
]
