import os
import numpy as np
from django.conf import settings
from django.shortcuts import render
from tensorflow.keras.preprocessing import image # type: ignore
import requests
import json

# Assuming your API endpoint for prediction
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
        img_modified = image.load_img(img_path, target_size=(224, 224))  # Adjust target_size based on your model
        img_array = image.img_to_array(img_modified)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        # Make prediction
        input_json = json.dumps({"data": img_array.tolist()})
        response = requests.post(url, data=input_json)        

        # Assuming the API returns JSON response with predictions
        context['result'] = response.json()
        context['img_path'] = os.path.join(settings.MEDIA_URL, img.name)  # Correcting img_path to use MEDIA_URL
        
        return render(request, 'app/result.html', context)

    return render(request, 'app/upload.html')


def home(request):
    return render(request, "app/index.html")
