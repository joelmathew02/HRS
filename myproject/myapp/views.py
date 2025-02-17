from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, LoginForm
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
import os
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

# Restrict access to superusers only
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin, login_url='login')  # Redirect non-admins to login
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})


def contact_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        reason = request.POST.get('reason')
        contact = request.POST.get('contact')

        # Send email (optional)
        send_mail(
            'Thank You for Contacting Us!',
            'Dear User,\n\nThank you for reaching out! We will get back to you soon.\n\nBest regards,\nHRS Team',
            'joelmathew20002@gmail.com',  # Replace with your email
            [email],
            fail_silently=False,
        )

        # Show success message

        return redirect('contact')  # Redirect to home page

    return render(request, 'contact.html')


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # Automatically log in the user after signing up
        return redirect('home')  # Redirect to upload page after signup

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after login
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')



def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_url = fs.url(filename)
        return render(request, 'upload.html', {'image_url': image_url})

    return render(request, 'upload.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def home_view(request):
    return render(request, 'home.html')

def delete_image(request):
    if request.method == "POST":
        image_url = request.POST.get("image_url")
        if image_url:
            image_name = os.path.basename(image_url)  # Get the filename
            image_path = os.path.join("media/uploads/", image_name)  # Adjust path if needed

            if default_storage.exists(image_path):
                default_storage.delete(image_path)  # Delete the file

        return redirect("upload")  # Redirect to the upload page

    return redirect("upload")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages


# Restrict access to superusers only
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})


@user_passes_test(is_admin, login_url='login')
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        user.is_active = False
        messages.success(request, f"{user.username} has been suspended.")
    else:
        user.is_active = True
        messages.success(request, f"{user.username} has been activated.")
    user.save()
    return redirect('admin_dashboard')

@user_passes_test(is_admin, login_url='login')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"User {user.username} has been deleted.")
    return redirect('admin_dashboard')


