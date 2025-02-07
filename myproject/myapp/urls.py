from django.urls import path
from .views import signup_view, login_view, logout_view, home_view
from django.contrib.auth.views import LogoutView
from .views import upload_image
from .views import upload_image, delete_image
from .views import contact_view
urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('upload/', upload_image, name='upload'),
    path('logout/', logout_view, name='logout'),
    path('upload/', upload_image, name='upload'),
    path('delete_image/', delete_image, name='delete_image'),
    path('contact/', contact_view, name='contact'),
]
