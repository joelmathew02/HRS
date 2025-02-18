from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.conf import settings
import os
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from docx import Document
from django.core.files.storage import FileSystemStorage

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
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"{user.username} has been {'activated' if user.is_active else 'suspended'}.")
    return redirect('admin_dashboard')

@user_passes_test(is_admin, login_url='login')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"User {user.username} has been deleted.")
    return redirect('admin_dashboard')

# User authentication views
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def home_view(request):
    return render(request, 'home.html')

def contact_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        reason = request.POST.get('reason')
        contact = request.POST.get('contact')
        send_mail(
            'Thank You for Contacting Us!',
            'Dear User,\n\nThank you for reaching out! We will get back to you soon.\n\nBest regards,\nHRS Team',
            'joelmathew20002@gmail.com',
            [email],
            fail_silently=False,
        )
        return redirect('contact')
    return render(request, 'contact.html')

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(f"uploads/{image.name}", image)  # Save inside 'uploads' folder
        image_url = fs.url(filename)
        return render(request, 'upload.html', {'image_url': image_url})

    return render(request, 'upload.html')

