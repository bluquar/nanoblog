from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'nanoblog.views.global_stream', name="home"),
    url(r'^following$', 'nanoblog.views.following', name="following"),
    url(r'^user/(?P<username>.*)$', 'nanoblog.views.user', name="user"),
    url(r'^profile_pic/(?P<id>\d+)$', 'nanoblog.views.get_profile_pic', name='profile_pic'),
    url(r'^follow/(?P<username>.*)$', 'nanoblog.views.follow', name="follow"),
    url(r'^unfollow/(?P<username>.*)$', 'nanoblog.views.unfollow', name="unfollow"),
    url(r'^add$', 'nanoblog.views.add', name="add"),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'nanoblog/login.html'}, name="login"),
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name="logout"),
    url(r'^register$', 'nanoblog.views.register', name="register"),
    url(r'^edit_profile$', 'nanoblog.views.edit_profile', name="edit_profile"),
    url(r'^add_comment$', 'nanoblog.views.add_comment', name='add_comment'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'nanoblog.views.confirm_registration', name='confirm'),
)