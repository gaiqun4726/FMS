from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^generateinitialfd$', views.generateInitialFD, name='generateInitialFD'),
    url(r'^getinitialfd$', views.getInitialFD, name='getInitialFD'),
    url(r'^home$', views.home, name='home'),
    url(r'^test$', views.test, name='test'),
]
