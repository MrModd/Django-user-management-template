from django.conf.urls import patterns, url, include
from rest_framework.authtoken import views as rest_views
from users import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	
	# Token authentication: token generator
	# Documentation here: http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
	# You can retrieve a user token making a POST to this REST API
	# with username and password in a JSON.
    # Example of REST queries with curl:
	# curl -X POST http://localhost:8000/rest/token/get/ -H "Content-Type: application/json" -d '{"username":"<username>", "password":"<password>"}'
	# curl -X POST http://localhost:8000/rest/token/renew/ -H "Content-Type: application/json" -H "Authorization: Token abcdefghijklmnopqrstuvwxyz0123456789abcd"
    url(r'^rest/token/get/$', rest_views.obtain_auth_token, name='gettoken'),
    url(r'^rest/token/renew/$', views.tokenRenewREST.as_view(), name='renewtoken'),
    
    
	# Access management
	url(r'^accounts/login/$', views.login, name='login'),
	url(r'^accounts/logout/$', views.logout, name='logout'),
	
	# User management
	url(r'^users/register/$', views.register, name='register'),
	url(r'^users/activation/$', views.activation, name='activation'),
	url(r'^users/reset/$', views.resetPassword, name='resetpassword'),
	url(r'^users/password/$', views.changePassword, name='password'),
	url(r'^users/delete/$', views.delete, name='delete'),
	url(r'^users/update/$', views.update, name='update'),
	url(r'^users/admin/$', views.adminUpdate, name='adminupdate'),
)
