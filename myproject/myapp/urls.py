from django.urls import path
from django.contrib import admin
from .views import signup_view, login_view, logout_view, home_view
from .views import upload_image, delete_image, contact_view
from .views import admin_dashboard, toggle_user_status, delete_user
from .views import upload_image, download_word_file

urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('upload/', upload_image, name='upload'),
    path('logout/', logout_view, name='logout'),
    path('delete_image/', delete_image, name='delete_image'),
    path('contact/', contact_view, name='contact'),

    # Django's built-in admin panel URL
    path('admin/', admin.site.urls),

    # Admin dashboard and user management routes
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('toggle-user-status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),

    path("download-word/", download_word_file, name="download_word"),
]
