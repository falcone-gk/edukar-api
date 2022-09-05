from django.urls import path, include
from account.views import LoginAPIView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

# from account import views

app_name = 'account'
urlpatterns = [
    path('', include('djoser.urls')),
    path('token/create', LoginAPIView.as_view(), name='token_create'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

### Explaining 'djoser.urls' Urls

# All urls have as prefix '/account/ path'
# In urls that is needed 'uid' that value is got in the email url sent.
# To check all the paths possible for djoser check the docs.

################## Create an account ###################
# Create user account: **'/users/'**, method: POST, fields: ('username', 'email', 'password', 're_password')
# After creating account, user has to activate account by verifying email. The url to verificate email is
# sent to the user email and has to click the link.
# When visiting the url, the page must send an POST request to: **'/users/activation/'**, fields: ('uid', 'token')
# Resend email url: **'/users/resend_activation/'**, method: POST, fields: ('email',)

################## Login and Refresh ###################
# Login url: '/jwt/create/', method: POST, fields: ('username', 'password')
# Return: {access: 'token used to authenticate user', refresh: 'token used to refresh token'}

# Refresh url: '/jwt/refresh/', method: POST, fields: ('refresh')
# Return: {access: 'token used to authenticate user'}

################## Reset Password ###################
# First we send an email to the user so user make a POST request to: **'/users/reset_password/**', fields: ('email',)
# User clicks link sent to its email and inside that view user makes a POST request to: **'/users/reset_password_confirm/',
# fields: ('uid', 'token', 'new_password', 're_new_password')
