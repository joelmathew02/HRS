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


from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import FileResponse
import os
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from docx import Document

# Load the TrOCR model & processor
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")


def preprocess_image(image_path):
    """ Preprocess the uploaded image: resize, grayscale, normalize """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
    img = cv2.resize(img, (640, 480))  # Resize to fit model input
    img = cv2.GaussianBlur(img, (5, 5), 0)  # Reduce noise
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Save the processed image
    processed_image_path = os.path.join(settings.MEDIA_ROOT, "processed_images", os.path.basename(image_path))
    cv2.imwrite(processed_image_path, img)
    return processed_image_path


def extract_text_from_image(image_path):
    """ Extract handwritten text using TrOCR """
    image = Image.open(image_path).convert("RGB")  # Open as RGB
    pixel_values = processor(images=image, return_tensors="pt").pixel_values

    with torch.no_grad():  # Disable gradient calculations (faster inference)
        generated_ids = model.generate(pixel_values)
        extracted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return extracted_text


def save_text_to_word(text):
    """ Save extracted text to a Word file """
    word_file_path = os.path.join(settings.MEDIA_ROOT, "output", "recognized_text.docx")

    doc = Document()
    doc.add_heading("Recognized Handwritten Text", level=1)
    doc.add_paragraph(text)
    doc.save(word_file_path)

    return word_file_path


def upload_image(request):
    """ Handles image upload, preprocessing, OCR, and saving text """
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]

        # Save original image
        image_path = os.path.join(settings.MEDIA_ROOT, "uploads", image_file.name)
        default_storage.save(image_path, ContentFile(image_file.read()))

        # Preprocess image
        preprocessed_image_path = preprocess_image(image_path)

        # Extract text using TrOCR
        extracted_text = extract_text_from_image(preprocessed_image_path)

        # Save extracted text to Word
        word_file_path = save_text_to_word(extracted_text)

        # Generate URLs to send to template
        image_url = os.path.join(settings.MEDIA_URL, "uploads", image_file.name)
        preprocessed_image_url = os.path.join(settings.MEDIA_URL, "processed_images", image_file.name)
        word_download_url = os.path.join(settings.MEDIA_URL, "output", "recognized_text.docx")

        return render(request, "upload.html", {
            "image_url": image_url,
            "preprocessed_image_url": preprocessed_image_url,
            "extracted_text": extracted_text,
            "word_download_url": word_download_url
        })

    return render(request, "upload.html")


from django.http import FileResponse
import os
from django.conf import settings

def download_word_file(request):
    """Allows users to download the Word file containing the extracted text"""
    file_path = os.path.join(settings.MEDIA_ROOT, "output", "recognized_text.docx")
    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename="recognized_text.docx")
    return render(request, "upload.html", {"error": "File not found"})

