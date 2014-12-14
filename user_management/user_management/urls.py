from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    
    # User management and main web application
    url(r'^', include('users.urls', namespace='users')),
)
