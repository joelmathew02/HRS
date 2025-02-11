from django.urls import path
from .views import signup_view, login_view, logout_view, home_view
from django.contrib.auth.views import LogoutView
from .views import upload_image
from .views import upload_image, delete_image
from .views import contact_view
from django.contrib import admin
from django.urls import path
from myapp.views import admin_dashboard
from django.urls import path
from .views import admin_dashboard, toggle_user_status, delete_user
from django.urls import path

urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('upload/', upload_image, name='upload'),
    path('logout/', logout_view, name='logout'),
    path('upload/', upload_image, name='upload'),
    path('delete_image/', delete_image, name='delete_image'),
    path('contact/', contact_view, name='contact'),
    path('admin/', admin.site.urls),  # Django's built-in admin panel
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('toggle-user-status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
]




