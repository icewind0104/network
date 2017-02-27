from django.conf.urls import url
from . import views

app_name = 'ipmanage'
urlpatterns = [
#    url(r'^ip/add/$', views.ip_add, name='ip_add'),
#    url(r'^ip/deal_add/$', views.ip_deal_add, name='ip_deal_add'),

#    url(r'^net/add/$', views.net_add, name='net_add'),
    url(r'^net/deal_add/$', views.net_deal_add, name='net_deal_add'),
    url(r'^$', views.net, name='net'),
    url(r'^login/$', views.login, name='login'),
    url(r'^login/deal$', views.login_deal, name='login_deal'),
    url(r'^logout/deal$', views.logout_deal, name='logout_deal'),
    url(r'^net/(?P<net_id>[0-9]+)/detail/$', views.net_detail, name='net_detail'),
#    url(r'^net/(?P<net_id>[0-9]+)/ip_add/$', views.net_ip_add, name='net_ip_add'),
#    url(r'^net/(?P<net_id>[0-9]+)/ip_detail/(?P<ip_id>[0-9]+)/$', views.net_ip_detail, name='net_ip_detail'),
    url(r'^net/(?P<net_id>[0-9]+)/deal_ip_modify/$', views.net_deal_ip_modify, name='net_deal_ip_modify'),
    url(r'^net/(?P<net_id>[0-9]+)/deal_muti_modify/$', views.net_deal_muti_modify, name='net_deal_muti_modify'),
    url(r'^net/deal_net_modify/$', views.net_deal_net_modify, name='net_deal_net_modify'),
]
