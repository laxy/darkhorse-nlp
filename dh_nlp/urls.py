from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dh_nlp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^submit$','dh_nlp.views.create_case'),
    url(r'^post_case_data$','dh_nlp.views.post_case_data'),
    url(r'^unresolved$','dh_nlp.views.pending_cases'),
    url(r'^rengine$','dh_nlp.views.recommend_cases'),
)
