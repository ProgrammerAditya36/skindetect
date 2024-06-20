from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import numpy as np
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
# Create your views here.
model_path = os.path.join(os.path.dirname(__file__), '../model_checkpoint.weights.keras')
print(model_path)
model = load_model(model_path)
@csrf_exempt
def predict_image(request):
    if request.method == 'POST' and request.FILES['image']:
        img = request.FILES['image']
        img_path = os.path.join('media', img.name)
        with open(img_path, 'wb+') as f:
            for chunk in img.chunks():
                f.write(chunk)
        image_array = image.img_to_array(image.load_img(img_path, target_size=(224, 224)))
        image_array = np.expand_dims(image_array, axis=0)
        predictions = model.predict(image_array)
        class_names = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis-like lesions', 'Dermatofibroma', 'Melanoma', 'Melanocytic nevi', 'Vascular lesions']
        predicted_class_index = np.argmax(predictions[0])
        predicted_class_name = class_names[predicted_class_index]
        result  = f'Predicted class: {predicted_class_name} with probability {predictions[0][predicted_class_index]:.4f}'
        return JsonResponse({'result': result})
    return render(request, 'app/upload.html')