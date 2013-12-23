from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views import generic


admin.autodiscover()


urlpatterns = patterns("",

    # Admin URLs.
    url(r"^admin/", include(admin.site.urls)),
    
    # There's no favicon here!
    url(r"^favicon.ico$", generic.RedirectView.as_view()),
    
)
