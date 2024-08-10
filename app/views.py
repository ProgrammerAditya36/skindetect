import os
import numpy as np
from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from .models import MongoUser
from tensorflow.keras.preprocessing import image #type: ignore
import requests
import json
import logging
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
logger = logging.getLogger(__name__)
from db_connection import addUser

# Assuming your FastAPI endpoint for prediction
url = "http://127.0.0.1:5000/predict"
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(request.POST)
        # Check if passwords match
        if password1 != password2:
            return render(request, 'app/register.html', {'error': 'Passwords do not match'})

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            return render(request, 'app/register.html', {'error': 'Email is already registered'})

        # Create new user
        user = User.objects.create_user(username=email, email=email, password=password1, first_name=first_name, last_name=last_name)
        user.save()
        # Add user to MongoDB
        addUser(request.POST)
        # Log in the user
        user = authenticate(username=email, password=password1)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'app/register.html', {'error': 'Registration failed'})
    
    return render(request, 'app/register.html')



def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Authenticate user with email
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'app/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'app/login.html')

def predict_image(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('image'):
        img = request.FILES['image']
        model_path = request.POST.get('model')  # Get selected model path
        
        img_path = os.path.join(settings.MEDIA_ROOT, img.name)
        
        # Save the uploaded file to MEDIA_ROOT
        with open(img_path, 'wb+') as destination:
            for chunk in img.chunks():
                destination.write(chunk)
        
        # Prepare the image for prediction
        img_modified = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img_modified)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        
        # Convert image data to list for FastAPI request
        img_data_list = img_array.tolist()
        
        # Prepare JSON data for FastAPI POST request
        input_data = {
            "data": img_data_list,
            "model_path": model_path  # Include model path in the request
        }
        
        # Make prediction request to FastAPI endpoint
        try:
            response = requests.post(url, json=input_data)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    context['result'] = result['result']
                    context['img_path'] = os.path.join(settings.MEDIA_URL, img.name)
                    context['probability'] = result['probability']
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    context['error'] = "Error decoding JSON response from the server."
            else:
                context['error'] = f"Error making prediction request: {response.status_code}"
        
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            context['error'] = f"Error making prediction request: {e}"
        
        return render(request, 'app/result.html', context)

    return render(request, 'app/upload.html')

def home(request):
    return render(request, "app/index.html")

def about(request):
    user_data = [{
        "name":"Adityaraj Singha",
        "img_src":"images/adityaraj.png",
        "descripttion":"B.Tech Engineer in MIT Manipal",
        "role":"Software Engineer",
        "link":"https://www.linkedin.com/in/adityaraj-singha-847b80262/"
    },{
        "name":"Neil George",
        "img_src":"images/neil.png",
        "descripttion":"B.Tech Engineer in MIT Manipal",
        "role":"Software Engineer",
        "link":"https://www.linkedin.com/in/neilgeorge1509/"
    },{
        "name":"Sriram Sunderrajan",
        "img_src":"images/sriram.png",
        "descripttion":"B.Tech Engineer in MIT Manipal",
        "role":"Software Engineer",
        "link":"https://www.linkedin.com/in/sriram-v-25y8/"

    },{
        "name":"Aditya Kinjawadekar",
        "img_src":"images/aditya.png",
        "descripttion":"B.Tech Engineer in MIT Manipal",
        "role":"Software Engineer",
        "link":"https://www.linkedin.com/in/adityaamit/"
    }
    ]
    context = {
        "team_members":user_data
    }
    return render(request, "app/about.html", context)

def contact(request):
    return render(request, "app/contact.html")
def user_logout(request):
    logout(request)
    return redirect('register')