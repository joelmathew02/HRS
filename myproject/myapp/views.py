from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
import os
from django.contrib import messages
from django.core.mail import send_mail

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


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # Automatically log in the user after signing up
        return redirect('upload')  # Redirect to upload page after signup

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('upload')  # Redirect to the upload page after login
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
