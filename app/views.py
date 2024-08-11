
import os
import json
import numpy as np
import pymongo
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from PIL import Image
import requests
import logging
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from db_connection import addUser, store_chat_message, chatCollection

logger = logging.getLogger(__name__)

# Assuming your FastAPI endpoint for prediction
main_url = "http://127.0.0.1:5000"
url_detect = f"{main_url}/detect"
url_predict = f"{main_url}/predict"
url_chat = f"{main_url}/chat"

def predict_image(request):
    diseases = [
        {
            "name": "Actinic keratoses",
            "symptoms": ["Rough, scaly patch on the skin", "Itching or burning"],
            "transmission": "Not contagious",
            "treatment": ["Cryotherapy", "Topical medications", "Photodynamic therapy"]
        },
        {
            "name": "Basal cell carcinoma",
            "symptoms": ["Pearly or waxy bump", "Flat, flesh-colored or brown scar-like lesion"],
            "transmission": "Not contagious",
            "treatment": ["Surgical excision", "Radiation therapy", "Topical treatments"]
        },
        {
            "name": "Benign keratosis-like lesions",
            "symptoms": ["Waxy, raised, wart-like growths", "Varied colors"],
            "transmission": "Not contagious",
            "treatment": ["Cryotherapy", "Curettage", "Laser therapy"]
        },
        {
            "name": "Dermatofibroma",
            "symptoms": ["Firm, raised nodule", "Varied colors"],
            "transmission": "Not contagious",
            "treatment": ["Surgical removal", "Cryotherapy"]
        },
        {
            "name": "Melanoma",
            "symptoms": ["New, unusual growth or a change in an existing mole", "Asymmetry, irregular border, varied color, diameter > 6mm"],
            "transmission": "Not contagious",
            "treatment": ["Surgical removal", "Immunotherapy", "Targeted therapy"]
        },
        {
            "name": "Melanocytic nevi",
            "symptoms": ["Small, dark skin growths", "Varied colors"],
            "transmission": "Not contagious",
            "treatment": ["Usually no treatment needed", "Surgical removal if necessary"]
        },
        {
            "name": "Vascular lesions",
            "symptoms": ["Red, purple, or blue marks on the skin", "Varied sizes and shapes"],
            "transmission": "Not contagious",
            "treatment": ["Laser therapy", "Sclerotherapy"]
        }
    ]

    context = {}
    if request.method == 'POST' and request.FILES.get('image'):
        img = request.FILES['image']
        img_path = os.path.join(settings.MEDIA_ROOT, img.name)

        # Save the uploaded file to MEDIA_ROOT
        with open(img_path, 'wb+') as destination:
            for chunk in img.chunks():
                destination.write(chunk)

        # Prepare the image for prediction using PIL
        img_modified = Image.open(img_path).resize((224, 224))
        img_array = np.array(img_modified)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array.astype('float32') / 255.0

        # Convert image data to list for FastAPI request
        img_data_list = img_array.tolist()

        # Prepare JSON data for FastAPI POST request
        input_data = {
            "data": img_data_list,
        }

        # Make prediction request to FastAPI endpoint
        try:
            response_detect = requests.post(url_detect, json=input_data)
            if response_detect.status_code == 200:
                try:
                    result_detect = response_detect.json()
                    detected_disease = result_detect['result']
                    if(detected_disease not in ["Benign","Malign"]):
                        context['result'] = "No Disease Detected"
                        context['img_path'] = os.path.join(settings.MEDIA_URL, img.name)
                        context['probability'] ="{:.4f}".format(result_detect['probability'])
                        return render(request, 'app/result.html', context)
                except json.JSONDecodeError as e:
                    context['error'] = "Error decoding JSON response from the server."
            response = requests.post(url_predict, json=input_data)

            if response.status_code == 200:
                try:
                    result = response.json()
                    detected_disease = result['result']
                    context['result'] = detected_disease
                    context['img_path'] = os.path.join(settings.MEDIA_URL, img.name)
                    context['probability'] = "{:.4f}".format(result['probability'])
                    for disease in diseases:
                        if disease['name'] == detected_disease:
                            context['disease'] = disease
                            break
                    
                except json.JSONDecodeError as e:
                    context['error'] = "Error decoding JSON response from the server."
            else:
                context['error'] = f"Error making prediction request: {response.status_code}"

        except requests.RequestException as e:
            context['error'] = f"Error making prediction request: {e}"

        return render(request, 'app/result.html', context)

    return render(request, 'app/upload.html')

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
def chat_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        # Store the user's message in MongoDB
        store_chat_message(request.user.id, user_message, sender='user')
        
        # Send the user's message to the chat API
        response = requests.post(url_chat, json={"message": user_message})
        
        if response.status_code == 200:
            try:
                result = response.json()
                bot_response = result['response']
                
                # Store the bot's response in MongoDB
                store_chat_message(request.user.id, bot_response, sender='bot')
                
                return JsonResponse({'bot_response': bot_response})
            except json.JSONDecodeError:
                return JsonResponse({'error': "Error decoding JSON response from the server."}, status=500)
        else:
            return JsonResponse({'error': f"Error making chat request: {response.status_code}"}, status=500)

    # For GET requests, you can either return an empty JsonResponse or render the chat template
    return JsonResponse({})
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