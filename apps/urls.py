from django.urls import include, path

urlpatterns = [
    path('account/', include('account.urls')),
    path('forum/', include('forum.urls')),
]