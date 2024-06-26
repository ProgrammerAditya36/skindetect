import os
import numpy as np
from django.conf import settings
from django.shortcuts import render
from tensorflow.keras.preprocessing import image #type: ignore
import requests
import json

# Assuming your FastAPI endpoint for prediction
url = "http://127.0.0.1:5000/predict"

def predict_image(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('image'):
        img = request.FILES['image']    
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
        input_data = {"data": img_data_list}
        
        
        # Make prediction request to FastAPI endpoint
        try:
            response = requests.post(url, json=input_data)
            
            if response.status_code == 200:
                try:
                    result = response.json(); 
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
    return render(request, "app/about.html")


def contact(request):
    return render(request, "app/contact.html")
