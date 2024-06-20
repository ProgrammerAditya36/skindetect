import os
import numpy as np
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load the Keras model
model_path = os.path.join(settings.BASE_DIR, 'model_checkpoint.weights.keras')


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
        model = load_model(model_path)
        predictions = model.predict(img_array)
        class_names = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis-like lesions', 'Dermatofibroma', 'Melanoma', 'Melanocytic nevi', 'Vascular lesions']
        predicted_class_index = np.argmax(predictions[0])
        predicted_class_name = class_names[predicted_class_index]
        result = f'Predicted class: {predicted_class_name} with probability {predictions[0][predicted_class_index]:.4f}'
        
        # Convert img_path to string for template rendering
        context['result'] = result

    return render(request, 'app/upload.html', context)
