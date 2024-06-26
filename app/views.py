import os
import numpy as np
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from tensorflow.keras.preprocessing import image # type: ignore
import requests
import json
url = "https://skin-detect-api.onrender.com/predict/"


@csrf_exempt
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
        img = image.load_img(img_path, target_size=(224, 224))  # Adjust target_size based on your model
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        # Make prediction
        input_json = json.dumps({"data": img_array.tolist()})
        response = requests.post(url, data=input_json)
        
        # Convert img_path to string for template rendering
        context['result'] = response.json()

    return render(request, 'app/upload.html', context)


def home(request):
    return render(request, "app/base.html")