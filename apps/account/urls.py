from account import views
from core.views import CustomAuthToken
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from account import views

app_name = "account"

router = DefaultRouter()
router.register(r"user-posts", views.OwnerPostAPIView, basename="user-posts")

urlpatterns = [
    path("", include("djoser.urls")),
    path("login", CustomAuthToken.as_view(), name="login"),
    path("logout", views.LogoutAPIView.as_view(), name="logout"),
    path("data", views.UserByTokenAPIView.as_view(), name="user-data"),
    path(
        "user/products/", views.UserProductsView.as_view(), name="user-products"
    ),
    path(
        "user/purchases/",
        views.UserPurchasesView.as_view(),
        name="user-purchases",
    ),
    # path('update-user', views.UpdateUserAPIView.as_view(), name='update-user'),
    # path('update-profile-user', views.UpdateUserProfileAPIView.as_view(), name='update-profile-user'),
    # path('image/upload', views.UploadUserImageAPIView.as_view(), name='image-upload')
]

urlpatterns += router.urls

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
